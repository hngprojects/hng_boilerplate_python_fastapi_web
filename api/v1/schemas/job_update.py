from pydantic import BaseModel, Field, validator
from typing import Optional

class JobUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    department: Optional[str] = Field(None, description="Job department")
    location: Optional[str] = Field(None, description="Job location")
    salary: Optional[str] = Field(None, description="Job salary")
    job_type: Optional[str] = Field(None, description="Job type")
    company_name: Optional[str] = Field(None, description="Company name")
