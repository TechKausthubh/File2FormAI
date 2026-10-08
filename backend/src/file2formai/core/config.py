from functools import lru_cache
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Typed runtime settings loaded only by the backend process."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="F2F_",
        extra="ignore",
    )

    application_name: str = "File2FormAI API"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr
    database_connect_timeout_seconds: float = Field(default=5, gt=0, le=30)
    database_pool_timeout_seconds: float = Field(default=5, gt=0, le=30)
    database_readiness_timeout_seconds: float = Field(default=5, gt=0, le=30)
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=5, ge=0, le=20)
    development_identity_enabled: bool = False
    development_user_id: UUID | None = None
    cors_origins: list[AnyHttpUrl] = Field(
        default_factory=lambda: [
            AnyHttpUrl("http://localhost:5173"),
            AnyHttpUrl("http://127.0.0.1:5173"),
        ]
    )

    @field_validator("database_url")
    @classmethod
    def require_async_postgresql_url(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().startswith("postgresql+asyncpg://"):
            raise ValueError("database URL must use the postgresql+asyncpg driver")
        return value

    @model_validator(mode="after")
    def validate_development_identity(self) -> "Settings":
        if self.development_identity_enabled and self.environment != "development":
            raise ValueError("development identity may only be enabled in development")
        if self.development_identity_enabled and self.development_user_id is None:
            raise ValueError("development_user_id is required when development identity is enabled")
        return self

    @property
    def sqlalchemy_database_url(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.cors_origins]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
