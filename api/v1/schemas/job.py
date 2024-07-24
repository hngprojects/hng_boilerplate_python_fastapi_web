from pydantic import BaseModel
from typing import Optional

class JobCreate(BaseModel):
    title: str
    description: str
    company: str
    location: str
    salary: Optional[float] = None
    is_active: Optional[bool] = True

class Job(JobCreate):
    id: int

    class Config:
        orm_mode = True
