from pydantic import BaseModel
from typing import Optional, List

class RegionCreate(BaseModel):
    region: str
    language: str
    timezone: str

class RegionUpdate(BaseModel):
    region: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

class RegionOut(BaseModel):
    id: str
    user_id: str
    region: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

    class Config:
        from_attributes = True