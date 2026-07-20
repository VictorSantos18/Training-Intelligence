from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    environment: Literal["development", "test", "production"]
    database_url: str
    frontend_url: AnyHttpUrl
    cors_origins_env: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )
    backend_cors_origins: str | None = None

    database_ssl_mode: Literal["auto", "disable", "require"] = "auto"
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=5, ge=0, le=20)
    database_pool_timeout: int = Field(default=30, ge=1, le=120)
    database_pool_recycle: int = Field(default=1800, ge=60, le=7200)

    supabase_url: str | None = None
    supabase_jwks_url: str | None = None
    supabase_jwt_issuer: str | None = None
    supabase_jwt_audience: str | None = None
    supabase_service_role_key: str | None = Field(default=None, repr=False)

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def validate_supported_database_url(cls, value: str) -> str:
        supported_prefixes = (
            "postgresql://",
            "postgresql+asyncpg://",
            "postgresql+psycopg://",
        )
        if not value.startswith(supported_prefixes):
            raise ValueError(
                "DATABASE_URL must use postgresql:// or postgresql+asyncpg://"
            )
        return value

    @field_validator("cors_origins_env", "backend_cors_origins")
    @classmethod
    def validate_cors_wildcard(cls, value: str | None) -> str | None:
        if value is None:
            return value
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if "*" in origins:
            raise ValueError("CORS origins cannot contain '*'")
        return value

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment != "production":
            return self

        required_values = {
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_JWKS_URL": self.supabase_jwks_url,
            "SUPABASE_JWT_ISSUER": self.supabase_jwt_issuer,
            "SUPABASE_JWT_AUDIENCE": self.supabase_jwt_audience,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise ValueError(
                "Missing required production settings: " + ", ".join(missing)
            )

        return self

    @property
    def cors_origins(self) -> list[str]:
        origins = [str(self.frontend_url).rstrip("/")]
        if self.cors_origins_env:
            origins.extend(self._parse_cors_origins(self.cors_origins_env))
        if self.backend_cors_origins:
            origins.extend(self._parse_cors_origins(self.backend_cors_origins))
        return list(dict.fromkeys(origins))

    def _parse_cors_origins(self, value: str) -> list[str]:
        return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
