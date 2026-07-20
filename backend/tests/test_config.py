import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.db.engine import build_async_database_url_and_connect_args


def make_settings(**overrides: object) -> Settings:
    values = {
        "environment": "development",
        "database_url": "postgresql+asyncpg://training:training@localhost:5433/training",
        "frontend_url": "http://localhost:3000",
        "supabase_url": None,
        "supabase_jwks_url": None,
        "supabase_jwt_issuer": None,
        "supabase_jwt_audience": None,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_environment_accepts_only_supported_values() -> None:
    with pytest.raises(ValidationError):
        make_settings(environment="staging")


def test_production_requires_supabase_auth_settings() -> None:
    with pytest.raises(ValidationError) as exc_info:
        make_settings(environment="production")

    assert "SUPABASE_URL" in str(exc_info.value)
    assert "SUPABASE_JWKS_URL" in str(exc_info.value)
    assert "SUPABASE_JWT_ISSUER" in str(exc_info.value)
    assert "SUPABASE_JWT_AUDIENCE" in str(exc_info.value)


def test_cors_origins_combines_frontend_and_extra_origins() -> None:
    settings = make_settings(
        cors_origins="http://localhost:3000, https://app.vercel.app/",
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "https://app.vercel.app",
    ]


def test_cors_origins_rejects_wildcard() -> None:
    with pytest.raises(ValidationError):
        make_settings(cors_origins="*")


def test_cors_origins_keeps_backend_cors_origins_compatibility() -> None:
    settings = make_settings(
        backend_cors_origins="http://127.0.0.1:3000, https://app.vercel.app/",
    )

    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://app.vercel.app",
    ]


def test_database_url_is_converted_to_asyncpg_with_ssl() -> None:
    settings = make_settings(
        environment="production",
        database_url="postgresql://user:pass@db.supabase.co:5432/postgres?sslmode=require",
        supabase_url="https://project.supabase.co",
        supabase_jwks_url="https://project.supabase.co/auth/v1/.well-known/jwks.json",
        supabase_jwt_issuer="https://project.supabase.co/auth/v1",
        supabase_jwt_audience="authenticated",
    )

    database_url, connect_args = build_async_database_url_and_connect_args(settings)

    assert database_url == "postgresql+asyncpg://user:pass@db.supabase.co:5432/postgres"
    assert connect_args == {"ssl": True}
