from pydantic import BaseModel
from uuid_extensions import uuid7
from typing import Dict, Any, Optional


class RoleCreate(BaseModel):
    name: str

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
        
        
class ResponseModel(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = None
