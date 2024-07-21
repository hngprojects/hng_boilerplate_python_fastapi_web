from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class JobBase(BaseModel):
    title: str
    description: str
    location: str
    job_type: str
    salary: int = Field(gt=0)
    company_name: str


class JobCreate(JobBase):
    pass


class JobResponseSchema(JobBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Update job post

class JobUpdate(BaseModel):
    title: str
    description: str
    location: str
    salary:float
    job_type:str
    company_name:str

class JobResponse(BaseModel):
    message: str
    status_code: int
    data: JobUpdate