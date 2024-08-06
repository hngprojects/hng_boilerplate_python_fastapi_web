from pydantic import EmailStr, BaseModel
from typing import Optional
from datetime import datetime


class PostTeamMemberSchema(BaseModel):
    """Pydantic Model for adding user to waitlist"""

    name: str
    role: str
    description: str
    picture_url: str
    
    team_type: Optional[str] = None
    facebook_link: Optional[str] = None
    instagram_link: Optional[str] = None
    xtwitter_link: Optional[str] = None




class TeamMemberCreateResponseSchema(PostTeamMemberSchema):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True