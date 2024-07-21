from pydantic import BaseModel

class DeactivateInviteBody(BaseModel):
    invitation_link: str
