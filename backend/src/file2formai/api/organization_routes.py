from typing import Annotated

from fastapi import APIRouter, Depends

from file2formai.api.dependencies import (
    get_membership_service,
    get_organization_service,
    get_request_context,
)
from file2formai.identity.context import RequestContext
from file2formai.identity.schemas import MembershipResponse
from file2formai.identity.service import MembershipService
from file2formai.organizations.schemas import (
    OrganizationResponse,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    OrganizationUpdate,
)
from file2formai.organizations.service import OrganizationService

router = APIRouter(prefix="/api/v1", tags=["organizations"])

ContextDependency = Annotated[RequestContext, Depends(get_request_context)]
OrganizationServiceDependency = Annotated[OrganizationService, Depends(get_organization_service)]
MembershipServiceDependency = Annotated[MembershipService, Depends(get_membership_service)]


@router.get("/organization", response_model=OrganizationResponse)
async def get_active_organization(
    context: ContextDependency,
    service: OrganizationServiceDependency,
) -> OrganizationResponse:
    return await service.get_active(context)


@router.patch("/organization", response_model=OrganizationResponse)
async def update_active_organization(
    update: OrganizationUpdate,
    context: ContextDependency,
    service: OrganizationServiceDependency,
) -> OrganizationResponse:
    return await service.update_active(context, update)


@router.get("/organization/settings", response_model=OrganizationSettingsResponse)
async def get_active_organization_settings(
    context: ContextDependency,
    service: OrganizationServiceDependency,
) -> OrganizationSettingsResponse:
    return await service.get_settings(context)


@router.patch("/organization/settings", response_model=OrganizationSettingsResponse)
async def update_active_organization_settings(
    update: OrganizationSettingsUpdate,
    context: ContextDependency,
    service: OrganizationServiceDependency,
) -> OrganizationSettingsResponse:
    return await service.update_settings(context, update)


@router.get("/members", response_model=list[MembershipResponse])
async def list_active_organization_members(
    context: ContextDependency,
    service: MembershipServiceDependency,
) -> list[MembershipResponse]:
    return await service.list_members(context)
