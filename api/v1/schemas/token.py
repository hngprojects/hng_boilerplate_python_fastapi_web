from typing import Optional
from pydantic import BaseModel, EmailStr


# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: str = None


class TokenRequest(BaseModel):
    email: EmailStr
    token: str


class OAuthToken(BaseModel):
    access_token: str
