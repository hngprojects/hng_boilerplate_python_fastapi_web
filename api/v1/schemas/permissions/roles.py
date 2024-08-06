from pydantic import BaseModel
from uuid_extensions import uuid7

class RoleCreate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True

class RoleAssignRequest(BaseModel):
    role_id: str
    
    
class RoleDeleteResponse(BaseModel):
    id: str
    message: str

    class Config:
        from_attributes = True