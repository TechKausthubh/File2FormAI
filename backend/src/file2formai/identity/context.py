import uuid
from dataclasses import dataclass

from file2formai.identity.models import MembershipRole


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Trusted tenant and role information resolved by an identity adapter."""

    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: MembershipRole


def require_org_admin(context: RequestContext) -> None:
    from file2formai.core.errors import PermissionDeniedError

    if context.role is not MembershipRole.ORG_ADMIN:
        raise PermissionDeniedError
