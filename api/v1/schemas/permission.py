from pydantic import BaseModel
from uuid import UUID
from typing import List

class PermissionModel(BaseModel):
    id: UUID
    name: str

class PermissionCreate(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    id: UUID
    name: str
    status_code: int
    message: str

    class Config:
        from_attributes = True

class PermissionList(BaseModel):
    permissions: List[PermissionModel]
    status_code: int
    message: str

    class Config:
        from_attributes = True