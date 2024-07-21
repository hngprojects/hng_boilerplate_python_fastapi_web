from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TestimonialCreate(BaseModel):
    firstname: str
    lastname: str
    content: str

class TestimonialResponse(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SuccessResponse(BaseModel):
    status: str
    message: str
    data: TestimonialResponse
