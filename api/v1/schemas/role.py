from pydantic import BaseModel
from typing import List, Optional

class RoleCreate(BaseModel):
    role_name: str
    organization_id: str
    permission_ids: List[int]