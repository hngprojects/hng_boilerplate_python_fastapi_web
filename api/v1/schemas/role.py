from pydantic import BaseModel
<<<<<<< HEAD
from typing import List


class RoleCreate(BaseModel):
    role_name: str
    organisation_id: str
    permission_ids: List[str]
=======
from typing import List, Optional
from uuid import UUID

class RoleCreate(BaseModel):
    role_name: str
    org_user: Optional[str] = None
    organization_id: UUID
    permission_ids: Optional[List[str]] = None
>>>>>>> upstream/backend


class ResponseModel(BaseModel):
    id: UUID
    role: str
    message: str
    status_code: int
