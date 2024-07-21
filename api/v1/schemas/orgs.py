from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
class OrganizationCreate(BaseModel):
    name: str
    description: str

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    description: str
    status_code: int
    message: str