from pydantic import BaseModel
from typing import Optional, List

class LanguageCreate(BaseModel):
    name: str

class LanguageUpdate(BaseModel):
    name: Optional[str] = None

class LanguageOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class TimezoneCreate(BaseModel):
    name: str

class TimezoneUpdate(BaseModel):
    name: Optional[str] = None

class TimezoneOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class RegionCreate(BaseModel):
    user_id: str
    name: str

class RegionUpdate(BaseModel):
    name: Optional[str] = None

class RegionOut(BaseModel):
    id: int
    user_id: str
    name: str

    class Config:
        from_attributes = True