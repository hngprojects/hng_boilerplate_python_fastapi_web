from pydantic import BaseModel, EmailStr
from typing import Dict
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

# class UserResponse(BaseModel):
#     id: uuid
#     email: str
#     first_name: str 
#     last_name: str 
#     created_at: datetime

#     class Config:
#         orm_mode = True
#         #from_attributes = True