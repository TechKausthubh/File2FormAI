import os
import uuid
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from file2formai.application import create_app
from file2formai.core.config import Settings
from file2formai.core.database import Database
from file2formai.core.models import Base
from file2formai.development.seed import DEVELOPMENT_ADMIN_USER_ID, seed_development_data
from file2formai.models import (  # noqa: F401
    EquipmentInstance,
    EquipmentModel,
    Membership,
    Organization,
    OrganizationSettings,
    User,
)


@pytest.fixture(scope="session")
def test_database_url() -> str:
    database_url = os.getenv("F2F_TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("F2F_TEST_DATABASE_URL is required for PostgreSQL integration tests")
    parsed = make_url(database_url)
    if parsed.database is None or not parsed.database.endswith("_test"):
        raise RuntimeError("integration tests require a database name ending in _test")
    return database_url


def build_settings(database_url: str, user_id: uuid.UUID) -> Settings:
    return Settings(
        environment="development",
        database_url=database_url,
        development_identity_enabled=True,
        development_user_id=user_id,
    )


@pytest_asyncio.fixture(autouse=True)
async def reset_test_database(test_database_url: str) -> AsyncIterator[None]:
    engine = create_async_engine(test_database_url)
    async with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            await connection.execute(table.delete())
    await engine.dispose()
    yield


@pytest_asyncio.fixture
async def seeded_database(test_database_url: str) -> None:
    database = Database(build_settings(test_database_url, DEVELOPMENT_ADMIN_USER_ID))
    try:
        async with database.session() as session:
            await seed_development_data(session)
    finally:
        await database.dispose()


@pytest.fixture
def admin_client(
    test_database_url: str,
    seeded_database: None,
) -> Iterator[TestClient]:
    app = create_app(build_settings(test_database_url, DEVELOPMENT_ADMIN_USER_ID))
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client_factory(test_database_url: str, seeded_database: None):
    def create(user_id: uuid.UUID) -> TestClient:
        return TestClient(create_app(build_settings(test_database_url, user_id)))

    return create
