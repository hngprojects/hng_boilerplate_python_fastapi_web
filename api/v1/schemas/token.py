from datetime import datetime
from typing import List, Optional
from api.v1.models.user import User
from pydantic import BaseModel, EmailStr

# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class EmailRequest(BaseModel):
    email: EmailStr

class TokenRequest(BaseModel):
    email: EmailStr
    token: str
    