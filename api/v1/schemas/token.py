from pydantic import BaseModel
from typing import List, Optional
from api.v1.models.user import User

# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(User):
    hashed_password: str