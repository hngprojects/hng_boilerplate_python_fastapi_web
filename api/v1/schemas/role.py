from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class RoleCreate(BaseModel):
    role_name: str
    org_user: Optional[str] = None
    organization_id: UUID
    permission_ids: Optional[List[str]] = None

class ResponseModel(BaseModel):
    id: UUID
    role: str
    message: str
    status_code: int