from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Any, Optional
from uuid_extensions import uuid7
import re
from api.v1.schemas.user import UserBase

class UserResponse(BaseModel):
    id: str

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
    user: UserResponse


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
  