from typing import Any

from sqlalchemy.engine import make_url

from app.core.config import Settings

SSL_MODES_REQUIRING_SSL = {"allow", "prefer", "require", "verify-ca", "verify-full"}


def build_async_database_url_and_connect_args(settings: Settings) -> tuple[str, dict[str, Any]]:
    url = make_url(settings.database_url)

    if url.drivername == "postgresql" or url.drivername.startswith("postgresql+"):
        url = url.set(drivername="postgresql+asyncpg")

    query = dict(url.query)
    ssl_mode = query.pop("sslmode", None)
    url = url.set(query=query)

    connect_args: dict[str, Any] = {}
    should_use_ssl = (
        settings.database_ssl_mode == "require"
        or (
            settings.database_ssl_mode == "auto"
            and (
                settings.environment == "production"
                or str(ssl_mode).lower() in SSL_MODES_REQUIRING_SSL
            )
        )
    )
    if should_use_ssl:
        connect_args["ssl"] = True

    return url.render_as_string(hide_password=False), connect_args
