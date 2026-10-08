from fastapi.testclient import TestClient

from file2formai.application import create_app
from file2formai.core.config import Settings
from file2formai.services.readiness import ReadinessService


class HealthyDatabase:
    async def ping(self) -> bool:
        return True


class UnavailableDatabase:
    async def ping(self) -> bool:
        raise ConnectionError("raw database details must not be returned")


def build_settings() -> Settings:
    return Settings(
        environment="test",
        database_url="postgresql+asyncpg://unit_test:unit_test@127.0.0.1:1/unit_test",
    )


def test_health_returns_exact_ok_payload() -> None:
    app = create_app(build_settings(), ReadinessService(HealthyDatabase()))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ok_when_database_probe_succeeds() -> None:
    app = create_app(build_settings(), ReadinessService(HealthyDatabase()))

    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_safe_503_when_database_probe_fails() -> None:
    app = create_app(build_settings(), ReadinessService(UnavailableDatabase()))

    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "raw database details" not in response.text
