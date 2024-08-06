from pydantic import BaseModel
from uuid_extensions import uuid7


class PermissionCreate(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    id: str
    name: str

    class Config:
        orm_mode = True

class PermissionAssignRequest(BaseModel):
    permission_id: str