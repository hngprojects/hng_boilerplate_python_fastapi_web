from datetime import datetime
# Remove the unused import statement
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
# Remove this commented out code
import re
from api.v1.schemas.user import UserBase


class ProfileBase(BaseModel):
    """Base profile schema"""

    id: str
    created_at: datetime
    pronouns: str
    job_title: str
    department: str
    social: str
    bio: str
    phone_number: str
    avatar_url: str
    recovery_email: Optional[EmailStr]
    user: UserBase
    created_at: datetime
    updated_at: datetime


class ProfileCreateUpdate(BaseModel):
    """Schema to create a profile"""

    pronouns: str
    job_title: str
    department: str
    social: str
    bio: str
    phone_number: str
    avatar_url: str
    recovery_email: Optional[EmailStr]

    @field_validator("phone_number")
    def phone_number_validator(cls, value):
        if not re.match(r"^\+?[1-9]\d{1,14}$", value):
            raise ValueError("Please use a valid phone number format")
        return value
