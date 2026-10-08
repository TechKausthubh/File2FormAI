from sqlalchemy.exc import IntegrityError

from file2formai.core.errors import ConflictError, ResourceNotFoundError
from file2formai.identity.context import RequestContext, require_org_admin
from file2formai.organizations.repository import OrganizationUnitOfWork
from file2formai.organizations.schemas import (
    OrganizationResponse,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    OrganizationUpdate,
)


class OrganizationService:
    def __init__(self, unit_of_work: OrganizationUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def get_active(self, context: RequestContext) -> OrganizationResponse:
        organization = await self._unit_of_work.organizations.get(context.organization_id)
        if organization is None:
            raise ResourceNotFoundError
        return OrganizationResponse.model_validate(organization)

    async def update_active(
        self,
        context: RequestContext,
        update: OrganizationUpdate,
    ) -> OrganizationResponse:
        require_org_admin(context)
        organization = await self._unit_of_work.organizations.get(context.organization_id)
        if organization is None:
            raise ResourceNotFoundError

        for field_name, value in update.model_dump(exclude_unset=True).items():
            setattr(organization, field_name, value)
        try:
            await self._unit_of_work.commit()
        except IntegrityError as error:
            await self._unit_of_work.rollback()
            raise ConflictError("Organization slug is already in use") from error
        await self._unit_of_work.refresh(organization)
        return OrganizationResponse.model_validate(organization)

    async def get_settings(
        self,
        context: RequestContext,
    ) -> OrganizationSettingsResponse:
        settings = await self._unit_of_work.organizations.get_settings(context.organization_id)
        if settings is None:
            raise ResourceNotFoundError
        return OrganizationSettingsResponse.model_validate(settings)

    async def update_settings(
        self,
        context: RequestContext,
        update: OrganizationSettingsUpdate,
    ) -> OrganizationSettingsResponse:
        require_org_admin(context)
        settings = await self._unit_of_work.organizations.get_settings(context.organization_id)
        if settings is None:
            raise ResourceNotFoundError

        values = update.model_dump(exclude_unset=True)
        if "logo_url" in values and values["logo_url"] is not None:
            values["logo_url"] = str(values["logo_url"])
        for field_name, value in values.items():
            setattr(settings, field_name, value)
        await self._unit_of_work.commit()
        return OrganizationSettingsResponse.model_validate(settings)
