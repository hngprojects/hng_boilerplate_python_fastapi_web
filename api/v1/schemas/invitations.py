from pydantic import BaseModel, EmailStr


class UserAddToOrganization(BaseModel):
    invitation_link: str


class InvitationCreate(BaseModel):
    user_email: EmailStr
    organization_id: str