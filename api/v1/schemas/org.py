from pydantic import BaseModel
from uuid import UUID
from typing import List

class OrganizationBase(BaseModel):
    id: UUID
    name: str
    description: str

    class Config:
        orm_mode = True

class OrganizationCreate(BaseModel):
    name: str
    description: str
