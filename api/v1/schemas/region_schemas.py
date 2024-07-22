from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

class RegionBase(BaseModel):
    region_code: str = Field(..., max_length=10)
    region_name: str = Field(..., max_length=100)
    status: str = Field("active", max_length=10)


class RegionCreate(BaseModel):
    region_code: str = Field(..., max_length=10)
    region_name: str = Field(..., max_length=100)
    status: str = Field("active", max_length=10)


class RegionResponse(RegionBase):
    id: uuid.UUID
    created_on: datetime
    modified_on: Optional[datetime] = None
    created_by: uuid.UUID

    class Config:
        from_attributes = True
