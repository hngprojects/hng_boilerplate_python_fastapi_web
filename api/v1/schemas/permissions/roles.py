from pydantic import BaseModel
from uuid_extensions import uuid7
from typing import Dict, Any, Optional


class RoleCreate(BaseModel):
    name: str
    is_builtin: bool = False  # Default to False for custom roles
    description: Optional[str] = None

class RoleResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class RoleAssignRequest(BaseModel):
    role_id: str


class RemoveUserFromRoleResponse(BaseModel):
    status_code: int
    message: str
    
    
class RoleDeleteResponse(BaseModel):
    id: str
    message: str

    class Config:
        from_attributes = True
        

class RoleUpdate(BaseModel):
    name: str
    is_builtin: bool
