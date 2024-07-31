from pydantic import BaseModel

class CreateTestimonial(BaseModel):
    content: str
    ratings: float = 0