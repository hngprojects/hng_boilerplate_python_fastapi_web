from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

class JobCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    
class JobResponse(BaseModel):
    job_id: uuid.UUID
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    employer: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    