from pydantic import BaseModel

class UserAddToOrganization(BaseModel):
    invitation_link: str


class InvitationCreate(BaseModel):
    user_id: str
    organization_id: str