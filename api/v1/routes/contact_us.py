from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.send_mail import send_contact_mail
from typing import Annotated
from api.core.responses import SUCCESS
from api.utils.success_response import success_response
from api.v1.services.contact_us import contact_us_service
from api.v1.schemas.contact_us import CreateContactUs
from api.v1.schemas.contact_us import ContactUsResponseSchema
from fastapi.encoders import jsonable_encoder
from api.v1.services.user import user_service
from api.v1.models import *

contact_us = APIRouter(prefix="/contact", tags=["Contact-Us"])


# CREATE
@contact_us.post(
    "",
    response_model=success_response,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Contact us message created successfully"},
        422: {"description": "Validation Error"},
    },
)
async def create_contact_us(
    data: CreateContactUs, db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    """Add a new contact us message."""
    new_contact_us_message = contact_us_service.create(db, data)

    # Send email to admin
    background_tasks.add_task(
        send_contact_mail, 
        context={
            "full_name": new_contact_us_message.full_name,
            "email": new_contact_us_message.email,
            "phone": new_contact_us_message.title,
            "message": new_contact_us_message.message,
        }
    )

    response = success_response(
        message=SUCCESS,
        data={"id": new_contact_us_message.id},
        status_code=status.HTTP_201_CREATED,
    )
    return response


@contact_us.get(
    "",
    response_model=success_response,
    status_code=200,
    responses={
        403: {"description": "Unauthorized"},
        500: {"description": "Server Error"},
    },
)
def retrieve_contact_us(
    db: Session = Depends(get_db),
    admin: User = Depends(user_service.get_current_super_admin),
):
    """
    Retrieve all contact-us submissions from database
    """

    all_submissions = contact_us_service.fetch_all(db)
    submissions_filtered = list(
        map(lambda x: ContactUsResponseSchema.model_validate(x), all_submissions)
    )
    if len(submissions_filtered) == 0:
        submissions_filtered = [{}]
    return success_response(
        message="Submissions retrieved successfully",
        status_code=200,
        data=jsonable_encoder(submissions_filtered),
    )
