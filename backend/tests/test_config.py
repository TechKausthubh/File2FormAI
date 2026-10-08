from uuid import UUID

import pytest
from pydantic import ValidationError

from file2formai.core.config import Settings


def test_cors_defaults_are_explicit_local_origins() -> None:
    settings = Settings(
        environment="test",
        database_url="postgresql+asyncpg://unit_test:unit_test@127.0.0.1:1/unit_test",
    )

    assert settings.allowed_cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert "*" not in settings.allowed_cors_origins


def test_database_url_requires_async_postgresql_driver() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="test", database_url="sqlite+aiosqlite:///test.db")


@pytest.mark.parametrize("environment", ["test", "production"])
def test_development_identity_is_rejected_outside_development(environment: str) -> None:
    with pytest.raises(ValidationError, match="development identity"):
        Settings(
            environment=environment,
            database_url="postgresql+asyncpg://unit_test:unit_test@127.0.0.1:1/unit_test",
            development_identity_enabled=True,
            development_user_id=UUID("20000000-0000-4000-8000-000000000001"),
        )


def test_development_identity_requires_a_user() -> None:
    with pytest.raises(ValidationError, match="development_user_id"):
        Settings(
            environment="development",
            database_url="postgresql+asyncpg://unit_test:unit_test@127.0.0.1:1/unit_test",
            development_identity_enabled=True,
        )
