from fastapi import (
    APIRouter,
    Depends,
    status
    )
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.services.contact_us import contact_us_service
from api.v1.schemas.contact_us import ContactUsResponseSchema
from fastapi.encoders import jsonable_encoder
from api.v1.models.user import User
from api.v1.services.user import user_service

contact_us = APIRouter(prefix='/contact', tags=['Contact-Us'])


@contact_us.get('', response_model=success_response, 
                 status_code=200,
                 responses=
                 {
                      403: {"description": "Unauthorized"},
                      500: {"description": "Server Error"}},
           )
def retrieve_contact_us(db: Session = Depends(get_db),
                              admin: User = Depends(user_service.get_current_super_admin)):
    """
    Retrieve all contact-us submissions from database
    """

    all_submissions = contact_us_service.fetch_all(db)
    submissions_filtered = list(map(lambda x: ContactUsResponseSchema(**x), all_submissions))

    return success_response(
        message = "Submissions retrieved successfully",
        status_code = 200,
        data = jsonable_encoder(submissions_filtered)
        )