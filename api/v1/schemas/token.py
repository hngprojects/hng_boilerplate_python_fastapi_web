from typing import Optional, Annotated
from pydantic import BaseModel, EmailStr, StringConstraints


# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: str = None


class TokenRequest(BaseModel):
    email: Optional[EmailStr] = None
    token: Annotated[
        str,
        StringConstraints(
            max_length=6,
            min_length=6,
            strip_whitespace=True
        )
    ]


class OAuthToken(BaseModel):
    access_token: str
