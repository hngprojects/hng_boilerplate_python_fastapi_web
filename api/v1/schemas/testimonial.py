from pydantic import BaseModel
from typing import Optional

class CreateTestimonial(BaseModel):
    content: str
    ratings: float = 0


class UpdateTestimonial(BaseModel):
    content: Optional[str] = None
    ratings: Optional[float] = None
    client_name: Optional[str] = None
    client_designation: Optional[str] = None
