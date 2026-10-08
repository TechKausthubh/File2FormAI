import uuid

from pydantic import BaseModel, ConfigDict

from file2formai.identity.models import MembershipRole


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: MembershipRole
    email: str
    display_name: str
