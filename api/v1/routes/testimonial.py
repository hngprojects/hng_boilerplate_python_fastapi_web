from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.models.testimonial import Testimonial
from api.utils.json_response import JsonResponseDict
from api.db.database import get_db

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
