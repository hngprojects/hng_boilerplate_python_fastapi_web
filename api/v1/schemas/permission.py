from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class PermissionBase(BaseModel):
    name: str
    description: Optional[str]

class PermissionCreate(PermissionBase):
    description: str

class PermissionUpdate(PermissionBase):
    description: Optional[str] = None

class Permission(PermissionBase):
    id: UUID
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
