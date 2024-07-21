from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from uuid_extensions import uuid7
from uuid import UUID
import re

class UserBase(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    created_at: datetime

class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    is_admin: bool

    @field_validator('password')
    def password_validator(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 3 characters long')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')
        return value

class SuccessResponseData(BaseModel):
    token: str
    user: UserBase

class SuccessResponse(BaseModel):
    statusCode: int = Field(201, example=201)
    message: str
    data: SuccessResponseData

class ErrorResponse(BaseModel):
    message: str
    error: str
    statusCode: int

class Token(BaseModel):
    access_token: str
    token_type: str