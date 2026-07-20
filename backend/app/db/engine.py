from typing import Any

from sqlalchemy.engine import make_url

from app.core.config import Settings

SSL_MODE_QUERY_VALUES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}


def build_async_database_url_and_connect_args(settings: Settings) -> tuple[str, dict[str, Any]]:
    url = make_url(settings.database_url)

    if url.drivername == "postgresql" or url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    url_ssl_mode = extract_ssl_mode_from_query(query)
    url = url.set(query=query)

    connect_args: dict[str, Any] = {}
    ssl_mode = resolve_database_ssl_mode(settings, url_ssl_mode)
    if ssl_mode != "disable":
        connect_args["ssl"] = ssl_mode

    return url.render_as_string(hide_password=False), connect_args


def extract_ssl_mode_from_query(query: dict[str, Any]) -> str | None:
    ssl_mode = query.pop("sslmode", None)
    ssl_value = query.pop("ssl", None)

    if ssl_mode:
        return str(ssl_mode).lower()

    if ssl_value is None:
        return None

    normalized_ssl_value = str(ssl_value).lower()
    if normalized_ssl_value in {"1", "true", "yes"}:
        return "require"
    if normalized_ssl_value in {"0", "false", "no"}:
        return "disable"
    if normalized_ssl_value in SSL_MODE_QUERY_VALUES:
        return normalized_ssl_value

    return None


def resolve_database_ssl_mode(settings: Settings, url_ssl_mode: str | None) -> str:
    if settings.database_ssl_mode != "auto":
        return settings.database_ssl_mode

    if url_ssl_mode in SSL_MODE_QUERY_VALUES:
        return url_ssl_mode

    if settings.environment == "production":
        return "require"

    return "disable"
