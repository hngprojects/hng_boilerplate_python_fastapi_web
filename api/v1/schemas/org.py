from pydantic import BaseModel
from uuid_extensions import uuid7
from uuid import UUID
from .user import UserBase
from typing import List


class OrganizationUsersResponse(BaseModel):
    org_id: UUID
    users: List[UserBase]

    class Config:
        from_attributes = True