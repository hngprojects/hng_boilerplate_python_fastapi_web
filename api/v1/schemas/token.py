from typing import List, Optional
from api.v1.models.user import User
from pydantic import BaseModel, EmailStr

# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TokenResponse(BaseModel):
    message: str
    data: dict

from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str