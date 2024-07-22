from pydantic import BaseModel
from typing import List

class PermissionBase(BaseModel):
    name: str
    description: str

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: str

    class Config:
        orm_mode: True

class PermissionsList(BaseModel):
    permissions: List[Permission]


class PermissionResponse(BaseModel):
    id: str  # Ensure UUIDs are represented as strings
    name: str
    description: str

    class Config:
        from_attributes: True

