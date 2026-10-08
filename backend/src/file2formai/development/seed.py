import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from file2formai.equipment.models import EquipmentInstance, EquipmentModel
from file2formai.identity.models import Membership, MembershipRole, User
from file2formai.organizations.models import Organization, OrganizationSettings

NORTHSTAR_ORGANIZATION_ID = uuid.UUID("10000000-0000-4000-8000-000000000001")
HARBORLINE_ORGANIZATION_ID = uuid.UUID("10000000-0000-4000-8000-000000000002")
DEVELOPMENT_ADMIN_USER_ID = uuid.UUID("20000000-0000-4000-8000-000000000001")
NORTHSTAR_TECHNICIAN_USER_ID = uuid.UUID("20000000-0000-4000-8000-000000000002")
HARBORLINE_TECHNICIAN_USER_ID = uuid.UUID("20000000-0000-4000-8000-000000000003")
NORTHSTAR_MODEL_ID = uuid.UUID("30000000-0000-4000-8000-000000000001")
HARBORLINE_MODEL_ID = uuid.UUID("30000000-0000-4000-8000-000000000002")
NORTHSTAR_INSTANCE_ID = uuid.UUID("40000000-0000-4000-8000-000000000001")
HARBORLINE_INSTANCE_ID = uuid.UUID("40000000-0000-4000-8000-000000000002")


async def seed_development_data(session: AsyncSession) -> None:
    """Upsert deterministic, domain-neutral development fixtures."""

    await session.execute(
        insert(Organization)
        .values(
            [
                {
                    "id": NORTHSTAR_ORGANIZATION_ID,
                    "name": "Northstar Field Services",
                    "slug": "northstar-field-services",
                },
                {
                    "id": HARBORLINE_ORGANIZATION_ID,
                    "name": "Harborline Manufacturing",
                    "slug": "harborline-manufacturing",
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[Organization.id],
            set_={
                "name": insert(Organization).excluded.name,
                "slug": insert(Organization).excluded.slug,
                "updated_at": func.now(),
            },
        )
    )
    await session.execute(
        insert(OrganizationSettings)
        .values(
            [
                {
                    "organization_id": NORTHSTAR_ORGANIZATION_ID,
                    "display_name": "Northstar Service Desk",
                    "logo_url": None,
                    "primary_color": "#164E63",
                    "secondary_color": "#67E8F9",
                    "technician_label": "Field Specialist",
                    "custom_settings": {"equipment_term": "asset"},
                },
                {
                    "organization_id": HARBORLINE_ORGANIZATION_ID,
                    "display_name": "Harborline Operations",
                    "logo_url": None,
                    "primary_color": "#7C2D12",
                    "secondary_color": "#FDBA74",
                    "technician_label": "Maintenance Technician",
                    "custom_settings": {"equipment_term": "machine"},
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[OrganizationSettings.organization_id],
            set_={
                "display_name": insert(OrganizationSettings).excluded.display_name,
                "logo_url": insert(OrganizationSettings).excluded.logo_url,
                "primary_color": insert(OrganizationSettings).excluded.primary_color,
                "secondary_color": insert(OrganizationSettings).excluded.secondary_color,
                "technician_label": insert(OrganizationSettings).excluded.technician_label,
                "custom_settings": insert(OrganizationSettings).excluded.custom_settings,
            },
        )
    )
    await session.execute(
        insert(User)
        .values(
            [
                {
                    "id": DEVELOPMENT_ADMIN_USER_ID,
                    "email": "developer.admin@file2formai.local",
                    "display_name": "Development Administrator",
                },
                {
                    "id": NORTHSTAR_TECHNICIAN_USER_ID,
                    "email": "technician@northstar.file2formai.local",
                    "display_name": "Northstar Technician",
                },
                {
                    "id": HARBORLINE_TECHNICIAN_USER_ID,
                    "email": "technician@harborline.file2formai.local",
                    "display_name": "Harborline Technician",
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[User.id],
            set_={
                "email": insert(User).excluded.email,
                "display_name": insert(User).excluded.display_name,
            },
        )
    )
    await session.execute(
        insert(Membership)
        .values(
            [
                {
                    "organization_id": NORTHSTAR_ORGANIZATION_ID,
                    "user_id": DEVELOPMENT_ADMIN_USER_ID,
                    "role": MembershipRole.ORG_ADMIN.value,
                },
                {
                    "organization_id": HARBORLINE_ORGANIZATION_ID,
                    "user_id": DEVELOPMENT_ADMIN_USER_ID,
                    "role": MembershipRole.ORG_ADMIN.value,
                },
                {
                    "organization_id": NORTHSTAR_ORGANIZATION_ID,
                    "user_id": NORTHSTAR_TECHNICIAN_USER_ID,
                    "role": MembershipRole.TECHNICIAN.value,
                },
                {
                    "organization_id": HARBORLINE_ORGANIZATION_ID,
                    "user_id": HARBORLINE_TECHNICIAN_USER_ID,
                    "role": MembershipRole.TECHNICIAN.value,
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[Membership.organization_id, Membership.user_id],
            set_={"role": insert(Membership).excluded.role},
        )
    )
    await session.execute(
        insert(EquipmentModel)
        .values(
            [
                {
                    "id": NORTHSTAR_MODEL_ID,
                    "organization_id": NORTHSTAR_ORGANIZATION_ID,
                    "manufacturer": "Atlas Dynamics",
                    "model_name": "PX-100 Pump",
                    "description": "Portable fluid-transfer pump used in field service operations.",
                    "metadata": {"category": "fluid-handling"},
                },
                {
                    "id": HARBORLINE_MODEL_ID,
                    "organization_id": HARBORLINE_ORGANIZATION_ID,
                    "manufacturer": "Meridian Systems",
                    "model_name": "CV-42 Conveyor",
                    "description": "Variable-speed conveyor used in manufacturing workflows.",
                    "metadata": {"category": "material-handling"},
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[EquipmentModel.id],
            set_={
                "organization_id": insert(EquipmentModel).excluded.organization_id,
                "manufacturer": insert(EquipmentModel).excluded.manufacturer,
                "model_name": insert(EquipmentModel).excluded.model_name,
                "description": insert(EquipmentModel).excluded.description,
                "metadata": insert(EquipmentModel).excluded.metadata,
                "updated_at": func.now(),
            },
        )
    )
    await session.execute(
        insert(EquipmentInstance)
        .values(
            [
                {
                    "id": NORTHSTAR_INSTANCE_ID,
                    "organization_id": NORTHSTAR_ORGANIZATION_ID,
                    "equipment_model_id": NORTHSTAR_MODEL_ID,
                    "serial_number": "NS-PX100-001",
                    "display_name": "Mobile Pump 01",
                    "metadata": {"service_region": "north"},
                },
                {
                    "id": HARBORLINE_INSTANCE_ID,
                    "organization_id": HARBORLINE_ORGANIZATION_ID,
                    "equipment_model_id": HARBORLINE_MODEL_ID,
                    "serial_number": "HL-CV42-001",
                    "display_name": "Assembly Conveyor 01",
                    "metadata": {"production_line": "line-a"},
                },
            ]
        )
        .on_conflict_do_update(
            index_elements=[EquipmentInstance.id],
            set_={
                "organization_id": insert(EquipmentInstance).excluded.organization_id,
                "equipment_model_id": insert(EquipmentInstance).excluded.equipment_model_id,
                "serial_number": insert(EquipmentInstance).excluded.serial_number,
                "display_name": insert(EquipmentInstance).excluded.display_name,
                "metadata": insert(EquipmentInstance).excluded.metadata,
                "updated_at": func.now(),
            },
        )
    )
    await session.commit()
