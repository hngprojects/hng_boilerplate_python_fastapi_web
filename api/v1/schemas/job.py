# api/v1/schemas/job_schema.py

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from datetime import datetime


class JobSchema(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True


class JobData(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str
    location: Optional[str] = None
    salary: Optional[float] = None
    job_type: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class JobSuccessResponse(BaseModel):
    statusCode: int = Field(200, example=200)
    message: str
    data: JobData
