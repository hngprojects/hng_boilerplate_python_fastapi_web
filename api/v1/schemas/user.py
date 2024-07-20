from pydantic import BaseModel, EmailStr
from typing import Dict
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

