from pydantic import BaseModel
from typing import Optional

class TestimonialBase(BaseModel):
    content: str
    client_designation: Optional[str] = None
    client_name: Optional[str] = None
    ratings: Optional[float] = None

class TestimonialCreate(TestimonialBase):
    pass

class TestimonialInDB(TestimonialBase):
    id: str    
    author_id: str
    comments: Optional[str] = None

    class Config:
        orm_mode = True
