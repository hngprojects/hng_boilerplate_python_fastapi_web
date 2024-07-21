from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TestimonialBase(BaseModel):
    client_name: str
    client_designation: str
    testimonial: Optional[str]
    rating: Decimal

class TestimonialCreate(TestimonialBase):
    pass

class Testimonial(TestimonialBase):
    id: int
    date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode: True
