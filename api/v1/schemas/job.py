from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

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