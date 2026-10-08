import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from file2formai.core.config import Settings
from file2formai.core.database import Database
from file2formai.development.seed import (
    DEVELOPMENT_ADMIN_USER_ID,
    HARBORLINE_INSTANCE_ID,
    HARBORLINE_MODEL_ID,
    HARBORLINE_ORGANIZATION_ID,
    NORTHSTAR_INSTANCE_ID,
    NORTHSTAR_MODEL_ID,
    NORTHSTAR_ORGANIZATION_ID,
    NORTHSTAR_TECHNICIAN_USER_ID,
    seed_development_data,
)
from file2formai.equipment.models import EquipmentInstance, EquipmentModel
from file2formai.identity.models import Membership, User
from file2formai.organizations.models import Organization, OrganizationSettings

pytestmark = pytest.mark.integration


def organization_headers(organization_id: uuid.UUID) -> dict[str, str]:
    return {"X-Development-Organization-ID": str(organization_id)}


@pytest.mark.asyncio
async def test_migration_and_seed_are_idempotent(test_database_url: str) -> None:
    database = Database(Settings(environment="test", database_url=test_database_url))
    try:
        async with database.session() as session:
            assert (
                await session.scalar(text("SELECT version_num FROM alembic_version"))
                == "20261007_0002"
            )
            assert (
                await session.scalar(
                    text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                )
                == "0.8.1"
            )
            await seed_development_data(session)
        async with database.session() as session:
            await seed_development_data(session)
        async with database.session() as session:
            assert await session.scalar(select(func.count()).select_from(Organization)) == 2
            assert await session.scalar(select(func.count()).select_from(OrganizationSettings)) == 2
            assert await session.scalar(select(func.count()).select_from(User)) == 3
            assert await session.scalar(select(func.count()).select_from(Membership)) == 4
            assert await session.scalar(select(func.count()).select_from(EquipmentModel)) == 2
            assert await session.scalar(select(func.count()).select_from(EquipmentInstance)) == 2
    finally:
        await database.dispose()


def test_active_organization_settings_and_members_are_tenant_scoped(
    admin_client: TestClient,
) -> None:
    northstar_headers = organization_headers(NORTHSTAR_ORGANIZATION_ID)
    harborline_headers = organization_headers(HARBORLINE_ORGANIZATION_ID)

    organization = admin_client.get("/api/v1/organization", headers=northstar_headers)
    northstar_settings = admin_client.get(
        "/api/v1/organization/settings", headers=northstar_headers
    )
    harborline_settings = admin_client.get(
        "/api/v1/organization/settings", headers=harborline_headers
    )
    members = admin_client.get("/api/v1/members", headers=northstar_headers)

    assert organization.status_code == 200
    assert organization.json()["slug"] == "northstar-field-services"
    assert northstar_settings.status_code == 200
    assert northstar_settings.json()["display_name"] == "Northstar Service Desk"
    assert harborline_settings.status_code == 200
    assert harborline_settings.json()["display_name"] == "Harborline Operations"
    assert members.status_code == 200
    assert {member["role"] for member in members.json()} == {"org_admin", "technician"}

    updated_organization = admin_client.patch(
        "/api/v1/organization",
        headers=northstar_headers,
        json={"name": "Northstar Field Operations"},
    )
    updated = admin_client.patch(
        "/api/v1/organization/settings",
        headers=northstar_headers,
        json={"primary_color": "#112233", "technician_label": "Service Specialist"},
    )
    unchanged_other_tenant = admin_client.get(
        "/api/v1/organization/settings", headers=harborline_headers
    )
    assert updated_organization.status_code == 200
    assert updated_organization.json()["name"] == "Northstar Field Operations"
    assert updated.status_code == 200
    assert updated.json()["primary_color"] == "#112233"
    assert unchanged_other_tenant.json()["primary_color"] == "#7C2D12"


def test_equipment_crud_validation_and_model_deletion_rule(
    admin_client: TestClient,
) -> None:
    headers = organization_headers(NORTHSTAR_ORGANIZATION_ID)
    invalid = admin_client.post(
        "/api/v1/equipment-models",
        headers=headers,
        json={"manufacturer": "   ", "model_name": "X", "description": ""},
    )
    assert invalid.status_code == 422

    created_model = admin_client.post(
        "/api/v1/equipment-models",
        headers=headers,
        json={
            "manufacturer": "Summit Equipment",
            "model_name": "HX-7",
            "description": "Hydraulic test unit",
            "metadata": {"category": "test-equipment"},
        },
    )
    assert created_model.status_code == 201
    model_id = created_model.json()["id"]
    assert created_model.json()["metadata"] == {"category": "test-equipment"}

    created_instance = admin_client.post(
        "/api/v1/equipment-instances",
        headers=headers,
        json={
            "equipment_model_id": model_id,
            "serial_number": "HX7-009",
            "display_name": "Hydraulic Tester 09",
            "metadata": {"bay": "3"},
        },
    )
    assert created_instance.status_code == 201
    instance_id = created_instance.json()["id"]

    blocked_delete = admin_client.delete(f"/api/v1/equipment-models/{model_id}", headers=headers)
    assert blocked_delete.status_code == 409

    updated_model = admin_client.patch(
        f"/api/v1/equipment-models/{model_id}",
        headers=headers,
        json={"description": "Updated hydraulic test unit"},
    )
    updated_instance = admin_client.patch(
        f"/api/v1/equipment-instances/{instance_id}",
        headers=headers,
        json={"display_name": "Hydraulic Tester 09A", "serial_number": None},
    )
    assert updated_model.status_code == 200
    assert updated_model.json()["description"] == "Updated hydraulic test unit"
    assert updated_instance.status_code == 200
    assert updated_instance.json()["serial_number"] is None

    assert (
        admin_client.delete(
            f"/api/v1/equipment-instances/{instance_id}", headers=headers
        ).status_code
        == 204
    )
    assert (
        admin_client.delete(f"/api/v1/equipment-models/{model_id}", headers=headers).status_code
        == 204
    )


def test_membership_verification_and_technician_mutation_denial(
    client_factory,
) -> None:
    with client_factory(NORTHSTAR_TECHNICIAN_USER_ID) as client:
        northstar_headers = organization_headers(NORTHSTAR_ORGANIZATION_ID)
        harborline_headers = organization_headers(HARBORLINE_ORGANIZATION_ID)

        assert client.get("/api/v1/equipment-models", headers=northstar_headers).status_code == 200
        assert (
            client.post(
                "/api/v1/equipment-models",
                headers=northstar_headers,
                json={"manufacturer": "A", "model_name": "B"},
            ).status_code
            == 403
        )
        assert client.get("/api/v1/members", headers=northstar_headers).status_code == 403
        assert (
            client.patch(
                "/api/v1/organization/settings",
                headers=northstar_headers,
                json={"primary_color": "#000000"},
            ).status_code
            == 403
        )
        assert client.get("/api/v1/organization", headers=harborline_headers).status_code == 403


def test_cross_tenant_resource_ids_are_indistinguishable_from_unknown_ids(
    admin_client: TestClient,
) -> None:
    headers = organization_headers(NORTHSTAR_ORGANIZATION_ID)
    unknown_id = uuid.UUID("ffffffff-ffff-4fff-8fff-ffffffffffff")

    model_list = admin_client.get("/api/v1/equipment-models", headers=headers)
    instance_list = admin_client.get("/api/v1/equipment-instances", headers=headers)
    assert model_list.status_code == 200
    assert {item["id"] for item in model_list.json()} == {str(NORTHSTAR_MODEL_ID)}
    assert instance_list.status_code == 200
    assert {item["id"] for item in instance_list.json()} == {str(NORTHSTAR_INSTANCE_ID)}

    for resource_id in (HARBORLINE_MODEL_ID, unknown_id):
        read = admin_client.get(f"/api/v1/equipment-models/{resource_id}", headers=headers)
        update = admin_client.patch(
            f"/api/v1/equipment-models/{resource_id}",
            headers=headers,
            json={"description": "must not change"},
        )
        delete = admin_client.delete(f"/api/v1/equipment-models/{resource_id}", headers=headers)
        assert (read.status_code, read.json()) == (404, {"detail": "Resource not found"})
        assert (update.status_code, update.json()) == (
            404,
            {"detail": "Resource not found"},
        )
        assert (delete.status_code, delete.json()) == (
            404,
            {"detail": "Resource not found"},
        )

    for resource_id in (HARBORLINE_INSTANCE_ID, unknown_id):
        assert (
            admin_client.get(
                f"/api/v1/equipment-instances/{resource_id}", headers=headers
            ).status_code
            == 404
        )
        assert (
            admin_client.patch(
                f"/api/v1/equipment-instances/{resource_id}",
                headers=headers,
                json={"display_name": "must not change"},
            ).status_code
            == 404
        )
        assert (
            admin_client.delete(
                f"/api/v1/equipment-instances/{resource_id}", headers=headers
            ).status_code
            == 404
        )


def test_cross_tenant_model_associations_are_rejected(admin_client: TestClient) -> None:
    headers = organization_headers(NORTHSTAR_ORGANIZATION_ID)
    create = admin_client.post(
        "/api/v1/equipment-instances",
        headers=headers,
        json={
            "equipment_model_id": str(HARBORLINE_MODEL_ID),
            "display_name": "Invalid association",
        },
    )
    update = admin_client.patch(
        f"/api/v1/equipment-instances/{NORTHSTAR_INSTANCE_ID}",
        headers=headers,
        json={"equipment_model_id": str(HARBORLINE_MODEL_ID)},
    )
    assert (create.status_code, create.json()) == (404, {"detail": "Resource not found"})
    assert (update.status_code, update.json()) == (404, {"detail": "Resource not found"})


@pytest.mark.asyncio
async def test_database_rejects_cross_tenant_model_association(
    test_database_url: str,
    seeded_database: None,
) -> None:
    database = Database(Settings(environment="test", database_url=test_database_url))
    try:
        with pytest.raises(IntegrityError):
            async with database.session() as session:
                session.add(
                    EquipmentInstance(
                        id=uuid.UUID("40000000-0000-4000-8000-000000000099"),
                        organization_id=NORTHSTAR_ORGANIZATION_ID,
                        equipment_model_id=HARBORLINE_MODEL_ID,
                        display_name="Invalid cross-tenant instance",
                        metadata_={},
                    )
                )
                await session.commit()
    finally:
        await database.dispose()


def test_missing_active_organization_is_rejected(admin_client: TestClient) -> None:
    response = admin_client.get("/api/v1/organization")
    assert response.status_code == 400
    assert response.json() == {"detail": "Active organization is required"}


def test_development_identity_disabled_requires_authentication(
    test_database_url: str,
    seeded_database: None,
) -> None:
    settings = Settings(
        environment="development",
        database_url=test_database_url,
        development_identity_enabled=False,
        development_user_id=DEVELOPMENT_ADMIN_USER_ID,
    )
    from file2formai.application import create_app

    with TestClient(create_app(settings)) as client:
        response = client.get(
            "/api/v1/organization",
            headers=organization_headers(NORTHSTAR_ORGANIZATION_ID),
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}
