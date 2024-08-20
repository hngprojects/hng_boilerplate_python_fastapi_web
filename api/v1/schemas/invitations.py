from pydantic import BaseModel, EmailStr


class UserAddToOrganisation(BaseModel):
    invitation_link: str


class InvitationCreate(BaseModel):
    user_email: EmailStr
    organisation_id: str
