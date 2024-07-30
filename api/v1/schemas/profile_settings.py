from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Optional[str]]] = None

class ProfileUpdate(BaseModel):
    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    recovery_email: Optional[EmailStr] = None

class UserAndProfileUpdate(UserProfileUpdate, ProfileUpdate):
    pass
