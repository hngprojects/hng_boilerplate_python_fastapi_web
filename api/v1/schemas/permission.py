from pydantic import BaseModel
from uuid import UUID

class PermissionCreate(BaseModel):
    name: str

class PermissionResponse(BaseModel):
    id: UUID
    name: str
    status_code: int
    message: str

    class Config:
        orm_mode = True