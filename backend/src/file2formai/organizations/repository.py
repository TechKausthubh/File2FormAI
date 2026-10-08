import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from file2formai.organizations.models import Organization, OrganizationSettings


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, organization_id: uuid.UUID) -> Organization | None:
        statement = select(Organization).where(Organization.id == organization_id)
        return (await self._session.scalars(statement)).one_or_none()

    async def get_settings(
        self,
        organization_id: uuid.UUID,
    ) -> OrganizationSettings | None:
        statement = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == organization_id
        )
        return (await self._session.scalars(statement)).one_or_none()


class OrganizationUnitOfWork:
    """Transaction boundary published by the organizations module."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.organizations = OrganizationRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def refresh(self, instance: object) -> None:
        await self.session.refresh(instance)
