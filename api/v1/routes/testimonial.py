from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services import testimonialCRUD
from api.v1.services.user import user_service
from api.v1.schemas import testimonial_schema
from api.v1.models import user

testimonial_route = APIRouter( tags=["Testimonials"])

@testimonial_route.post("/testimonials", response_model=testimonial_schema.TestimonialInDB)
def create_testimonial(
    testimonial: testimonial_schema.TestimonialCreate, 
    db: Session = Depends(get_db), 
    current_user: user.User = Depends(user_service.get_current_user)
):
    return testimonialCRUD.create_testimonial(db=db, testimonial_create=testimonial, author_id=current_user.id)

