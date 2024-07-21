from pydantic import BaseModel, EmailStr,field_validator
from typing import Dict
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

    @field_validator('password')
    def password_length(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value

