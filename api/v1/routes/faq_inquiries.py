from fastapi import APIRouter, status, BackgroundTasks, Depends
from api.core.responses import SUCCESS
from api.db.database import get_db
from api.utils.send_mail import send_faq_inquiry_mail
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.faq_inquiries import CreateFAQInquiry
from api.v1.services.faq_inquiries import faq_inquiries_service
from api.v1.services.user import user_service
from sqlalchemy.orm import Session
from typing import Annotated

faq_inquiries = APIRouter(prefix="/faq-inquiries", tags=["FAQ-Inquiries"])

# CREATE
@faq_inquiries.post(
    "",
    response_model=success_response,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "FAQ Inquiry created successfully"},
        422: {"description": "Validation Error"},
    },
)
async def create_faq_inquiry(
    data: CreateFAQInquiry, db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    """Add a new FAQ Inquiry."""
    new_faq_inquiry = faq_inquiries_service.create(db, data)

    # Send email to admin
    background_tasks.add_task(
        send_faq_inquiry_mail, 
        context={
            "full_name": new_faq_inquiry.full_name,
            "email": new_faq_inquiry.email,
            "message": new_faq_inquiry.message,
        }
    )

    response = success_response(
        message=SUCCESS,
        data={"id": new_faq_inquiry.id},
        status_code=status.HTTP_201_CREATED,
    )
    return response

# READ
@faq_inquiries.get(
    "",
    response_model=success_response,
    status_code=200
)
async def get_all_faq_inquiries(
    db: Annotated[Session, Depends(get_db)],
    admin: User = Depends(user_service.get_current_super_admin),
):
    """Fetch all FAQ Inquiries."""
    faq_inquiries = faq_inquiries_service.fetch_all(db)
    response = success_response(
        message=SUCCESS,
        data=faq_inquiries,
        status_code=status.HTTP_200_OK,
    )
    return response