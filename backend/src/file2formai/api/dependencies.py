import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from file2formai.core.config import Settings
from file2formai.core.errors import AuthenticationRequiredError, PermissionDeniedError
from file2formai.equipment.repository import EquipmentUnitOfWork
from file2formai.equipment.service import EquipmentService
from file2formai.identity.context import RequestContext
from file2formai.identity.repository import MembershipRepository
from file2formai.identity.service import MembershipService
from file2formai.organizations.repository import OrganizationUnitOfWork
from file2formai.organizations.service import OrganizationService
from file2formai.services.readiness import ReadinessService


def get_readiness_service(request: Request) -> ReadinessService:
    return request.app.state.readiness_service


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.session() as session:
        yield session


async def get_request_context(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
    active_organization_id: Annotated[
        uuid.UUID | None,
        Header(alias="X-Development-Organization-ID"),
    ] = None,
) -> RequestContext:
    if not settings.development_identity_enabled or settings.development_user_id is None:
        raise AuthenticationRequiredError
    if active_organization_id is None:
        raise HTTPException(status_code=400, detail="Active organization is required")

    membership = await MembershipRepository(session).get(
        active_organization_id,
        settings.development_user_id,
    )
    if membership is None:
        raise PermissionDeniedError
    return RequestContext(
        user_id=settings.development_user_id,
        organization_id=active_organization_id,
        role=membership.role,
    )


def get_organization_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationService:
    return OrganizationService(OrganizationUnitOfWork(session))


def get_membership_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MembershipService:
    return MembershipService(MembershipRepository(session))


def get_equipment_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EquipmentService:
    return EquipmentService(EquipmentUnitOfWork(session))
