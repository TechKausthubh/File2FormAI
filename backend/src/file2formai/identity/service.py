from file2formai.identity.context import RequestContext, require_org_admin
from file2formai.identity.repository import MembershipRepository
from file2formai.identity.schemas import MembershipResponse


class MembershipService:
    def __init__(self, repository: MembershipRepository) -> None:
        self._repository = repository

    async def list_members(self, context: RequestContext) -> list[MembershipResponse]:
        require_org_admin(context)
        memberships = await self._repository.list_for_organization(context.organization_id)
        return [
            MembershipResponse(
                organization_id=membership.organization_id,
                user_id=membership.user_id,
                role=membership.role,
                email=membership.user.email,
                display_name=membership.user.display_name,
            )
            for membership in memberships
        ]
