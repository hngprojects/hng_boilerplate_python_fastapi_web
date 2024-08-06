from pydantic import EmailStr, BaseModel
from typing import Optional
from datetime import datetime


class PostJobSchema(BaseModel):
    """Pydantic Model for adding user to waitlist"""

    title: str
    description: str
    department: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None


class AddJobSchema(PostJobSchema):
    author_id: str


class JobCreateResponseSchema(PostJobSchema):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class UpdateJobSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None