from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict
import re
from api.v1.schemas.user import UserBase

class ProfileBase(BaseModel):
    '''Base profile schema'''

    id: str
    created_at: datetime
    pronouns: str 
    job_title: str
    department: str
    social: str
    bio: str
    phone_number:str
    avatar_url:str
    recovery_email:Optional[EmailStr]
    user: UserBase


class ProfileCreateUpdate(BaseModel):
    '''Schema to create a profile'''
   
    pronouns: str 
    job_title: str
    department: str
    social: str
    bio: str
    phone_number:str
    avatar_url:str
    recovery_email:Optional[EmailStr]

    @field_validator('phone_number')
    def phone_number_validator(cls, value):
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise ValueError('Please use a valid phone number format')
        return value
  


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