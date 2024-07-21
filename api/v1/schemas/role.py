from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class RoleCreate(BaseModel):
    role_name: str
    organization_id: UUID
    permission_ids: List[str]

class ResponseModel(BaseModel):
    id: UUID
    role: str
    message: str
    status_code: int