from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi_pagination import Page, paginate, Params, add_pagination
from sqlalchemy.orm import Session
from api.v1.models.testimonials import Testimonial as TestimonialModel
from api.v1.schemas.testimonial import Testimonial
from api.db.database import get_db
from .auth import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.v1.models.user import User

route = APIRouter()

@route.get("/api/testimonials")
async def get_testimonials(
    db: Session = Depends(get_db),
    params: Params = Depends(),
    current_user: User = Security(get_current_user)
):
    testimonials = db.query(TestimonialModel).all()
    
    if not testimonials:
        return {
                "message": "Error retrieving testimonials",
                "status_code": 500
        }
        
    data = paginate(testimonials, params)
    
    return{
        "message": "Testimonials retrieved successfully",
        "status_code": 200,
        "data": data.items,
        "pagination": {
            "current_page": data.page,
            "per_page": data.size,
            "total_pages": data.pages,
            "total_testimonials": data.total
    }
}

# Add pagination to the route
add_pagination(route)
