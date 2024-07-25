from fastapi import Depends, HTTPException, APIRouter, Request, Response, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from api.utils.success_response import success_response
from api.v1.models.testimonial import Testimonial
from api.v1.models.user import User
# from api.v1.schemas.user import DeactivateUserSchema, UserBase
from api.db.database import get_db
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service
from api.utils.json_response import JsonResponseDict


testimonial = APIRouter(prefix='/testimonials', tags=['Testimonials'])


@testimonial.delete("/", response_class=JsonResponseDict)
async def delete_all_testimonials(db: Session = Depends(get_db)):
    """
    Deletes all testimonials
    """
    try:
        db.query(Testimonial).delete()
        db.commit()
        return JsonResponseDict(
            message="All testimonials deleted successfully",
            data={},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
