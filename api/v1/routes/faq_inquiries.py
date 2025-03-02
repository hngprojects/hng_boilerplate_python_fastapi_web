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
from fastapi import Request

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
    data: CreateFAQInquiry,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Add a new FAQ Inquiry for both visitors and authenticated users."""
    access_token = request.headers.get("Authorization")
    current_user = user_service.get_current_user_or_none(access_token, db)
    user_id = current_user.id if current_user else None  # Set user_id only if authenticated

    new_faq_inquiry = faq_inquiries_service.create(db, data, user_id)  # Pass user_id (None for visitors)

    # Send email to admin
    background_tasks.add_task(
        send_faq_inquiry_mail,
        context={
            "full_name": new_faq_inquiry.full_name,
            "email": new_faq_inquiry.email,
            "message": new_faq_inquiry.message,
        },
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


# DELETE
@faq_inquiries.delete(
    "/{id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "FAQ inquiry deleted successfully."},
        401: {"description": "Not authorized."},
        404: {"description": "FAQ inquiry does not exist."},
        500: {"description": "Internal server error."},
    },
)
async def delete_faq_inquiry(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(user_service.get_current_user),
):
    """Delete a FAQ inquiry. Only the owner or an admin can delete it."""
    # Retrieve the FAQ inquiry by id
    inquiry = faq_inquiries_service.fetch(db, id)
    if not inquiry:
        return {
            "status": "error",
            "status_code": status.HTTP_404_NOT_FOUND,
            "message": "FAQ Inquiry does not exist.",
            "data": {},
        }

    # Check if the current user is the owner of the inquiry or an admin
    if inquiry.user_id != current_user.id and not current_user.is_superadmin:
        return {
            "status": "error",
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "message": "Not authorized.",
            "data": {},
        }

    try:
        # Delete the inquiry and commit the transaction
        faq_inquiries_service.delete(db, id)
        db.commit()
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error. Please try again later.",
            "data": {},
        }

    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "FAQ inquiry deleted successfully.",
        "data": {},
    }