from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Previously 'orm_mode = True'
