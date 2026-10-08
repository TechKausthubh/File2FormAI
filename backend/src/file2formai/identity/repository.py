import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from file2formai.identity.models import Membership


class MembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Membership | None:
        statement = select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user_id,
        )
        return (await self._session.scalars(statement)).one_or_none()

    async def list_for_organization(
        self,
        organization_id: uuid.UUID,
    ) -> list[Membership]:
        statement = (
            select(Membership)
            .where(Membership.organization_id == organization_id)
            .order_by(Membership.user_id)
        )
        return list((await self._session.scalars(statement)).all())
