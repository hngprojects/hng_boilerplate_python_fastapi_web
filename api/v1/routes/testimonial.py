from fastapi import APIRouter, Depends, Security, HTTPException, Query
from fastapi_pagination import Page, Params, add_pagination
from sqlalchemy.orm import Session
from datetime import datetime
from api.v1.models.testimonials import Testimonial as TestimonialModel
from api.v1.schemas.testimonial import Testimonial
from api.db.database import get_db
from .auth import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.v1.models.user import User

testimonial = APIRouter()

@testimonial.get("/api/testimonials")
async def get_testimonials(
    db: Session = Depends(get_db),
    params: Params = Depends(),
    current_user: User = Security(get_current_user),
    rating: int = Query(None, ge=1, le=5, description="Rating of the testimonial (1-5)"),
    date: str = Query(None, description="Date of the testimonial in YYYY-MM-DD format")
):
    if rating is not None and (rating < 1 or rating > 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")

    query = db.query(TestimonialModel)

    if rating:
        query = query.filter(TestimonialModel.rating == rating)
    
    if date:
        query = query.filter(TestimonialModel.date == date)

    total = query.count()
    total_pages = (total + params.size - 1) // params.size

    if params.page > total_pages:
        params.page = total_pages

    query = query.offset((params.page - 1) * params.size).limit(params.size)
    testimonials = query.all()

    return {
        "message": "Testimonials retrieved successfully",
        "status_code": 200,
        "data": testimonials,
        "pagination": {
            "current_page": params.page,
            "per_page": params.size,
            "total_pages": total_pages,
            "total_testimonials": total
        }
    }

# Add pagination to the route
add_pagination(testimonial)