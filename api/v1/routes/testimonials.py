from fastapi import Depends, Query, APIRouter, status, HTTPException
from api.v1.services.user import user_service
from api.utils.json_response import JsonResponseDict
from fastapi.responses import JSONResponse
from api.db.database import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.services.rate_limiter import rate_limiter
from api.v1.models.testimonial import Testimonial
from api.v1.schemas.testimonial import PaginatedTestimonials
from api.v1.routes.testimonial import testimonial


@testimonial.get("", response_model=PaginatedTestimonials,
                        dependencies=[Depends(rate_limiter)])
async def get_testimonials(page: int = Query(1, ge=1),
                           current_user: str = Depends(
                               user_service.get_current_user),
                           db: Session = Depends(get_db)):
    """
    Retrieves client testimonials

    Args:
        page (int, optional): page data to return. Defaults to Query(1, ge=1).
            current_user (str, optional): current authenticated client
            making the request. Defaults to Depends(get_current_user).
        db (Session, optional): Current database session.
            Defaults to Depends(get_db).


    Returns:
        clients testimonials
    """
    # calculate start and end points for pagination
    per_page = 3
    start = (page - 1) * per_page
    end = start + per_page

    try:
        # Retrieve testimonials from database
        testimonials = db.query(Testimonial).all()

        # Total testimonials pages
        total_pages = (len(testimonials) + per_page - 1) // per_page
        # Total testimonial
        total_testimonial = len(testimonials)

        # get needed data only
        testimonials = testimonials[start:end]
        if not testimonials:
            return JSONResponse(status_code=404, content={
                'status_code': 404, 'message': "No testimonials found"})

        # paginated response
        response = {
            "message": "Testimonials retrieved successfully",
            "status_code": 200,
            "data": [testimonial.to_dict() for testimonial in testimonials],
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "total_testimonials": total_testimonial
            }
        }
        return JSONResponse(content=response, status_code=200)
    except Exception as ex:
        return JsonResponseDict(
            status_code=500,
            message='Error retrieving testimonials',
            error=[str(ex)]
        )
