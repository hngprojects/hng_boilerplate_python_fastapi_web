from pydantic import BaseModel
from uuid import UUID
from typing import List

class Permission(BaseModel):
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
        orm_mode = True

class PermissionList(BaseModel):
    permissions = List[Permission]
    status_code: int
    message: str