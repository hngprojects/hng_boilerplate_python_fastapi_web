import re
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid_extensions import uuid7


class UserBase(BaseModel):
    '''Base user schema'''

    id: str
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    created_at: datetime

class UserCreate(BaseModel):
    '''Schema to create a user'''
    
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr

    @field_validator('password')
    def password_validator(cls, value):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise ValueError('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit and one special character.')
        return value

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    '''Schema to structure token data'''
    
    id: Optional[Any]



class DeactivateUserSchema(BaseModel):
    '''Schema for deactivating a user'''

    reason: Optional[str] = None
    confirmation: bool
