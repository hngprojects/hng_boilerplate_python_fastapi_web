from pydantic import BaseModel
from typing import List, Optional

class RoleCreate(BaseModel):
    role_name: str
    organization_id: str
    permission_ids: List[int]



# Pydantic models for request and response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(User):
    hashed_password: str