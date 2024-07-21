from pydantic import BaseModel, Field

class DeactivateInviteBody(BaseModel):
    invitation_link: str = Field(
        ...,
        description='The invitation link must follow the format invite_[invitation_id]',
        example='invite_12345'
    )
