from pydantic import BaseModel

class JobCreate(BaseModel):
    title: str
    description: str
    company: str
    location: str
    salary: float
