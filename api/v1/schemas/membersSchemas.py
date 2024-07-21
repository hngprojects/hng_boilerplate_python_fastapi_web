from pydantic import BaseModel
from typing import List, Optional

class Member(BaseModel):
    user_id: str
    organization_id: str
    user_email: str
    organization_name: str


class JsonResponseDict(BaseModel):
    total: int
    page: int
    limit: int
    prev: Optional[str]
    next: Optional[str]
    users: List[Member]
