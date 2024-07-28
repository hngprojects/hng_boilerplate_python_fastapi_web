from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    salary: Optional[str]
    job_type: Optional[str]
    company_name: Optional[str]

    class Config:
        from_attributes = True
class JobResponse(BaseModel):
    title: str
    description: str
    location: str
    salary: str
    job_type: str
    company_name: str
    created_at: datetime
    updated_at: datetime
