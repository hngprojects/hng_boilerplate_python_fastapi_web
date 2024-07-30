import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    """Base user schema"""

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime


class UserCreate(BaseModel):
    """Schema to create a user"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, value):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            value,
        ):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit and one special character."
            )
        return value
    

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class EmailRequest(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema to structure token data"""

    id: Optional[str]


class DeactivateUserSchema(BaseModel):
    """Schema for deactivating a user"""

    reason: Optional[str] = None
    confirmation: bool


class ChangePasswordSchema(BaseModel):
    """Schema for changing password of a user"""

    old_password: str
    new_password: str


class ChangePwdRet(BaseModel):
    """schema for returning change password response"""

    status_code: int
    message: str

class MagicLinkRequest(BaseModel):
    '''Schema for magic link creation'''

    email: EmailStr

class MagicLinkResponse(BaseModel):
    '''Schema for magic link respone'''

    message: str
