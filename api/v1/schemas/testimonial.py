from pydantic import BaseModel
from typing import List


class Testimonial(BaseModel):
    id: int
    client_name: str
    client_designation: str
    testimonial: str
    rating: int
    date: str


class PaginatedTestimonials(BaseModel):
    testimonials: List[Testimonial]
    pagination: dict
