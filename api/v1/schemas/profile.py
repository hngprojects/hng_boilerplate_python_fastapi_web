from pydantic import BaseModel
from typing import Optional
from pydantic.types import Emailstr
from api.models.user import UserBase


class ProfileBase(BaseModel):
    """Base profile schema"""
    
    id:str
    pronouns: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    social: Optional[str]  # Assuming JSON or similar data type
    bio: Optional[str]
    phone_number: Optional[str]
    avatar_url: Optional[str]
    recovery_email: Optional[Emailstr]
    user: UserBase


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: str
    user_id: str

    class Config:
        orm_mode = True
