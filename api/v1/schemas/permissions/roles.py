from pydantic import BaseModel
from uuid_extensions import uuid7

class RoleCreate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class RoleAssignRequest(BaseModel):
    role_id: str