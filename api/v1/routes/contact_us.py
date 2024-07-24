from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.contact_us import ContactUsCreate, ContactUsResponse
from api.v1.services.contact_us import ContactUsService

contact_us = APIRouter(prefix="/contact-us", tags=["Contact Us"])


@contact_us.post(
    "",
    response_model=ContactUsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact_message(
    contact_message: ContactUsCreate,
    db: Session = Depends(get_db),
):
    """Create a contact message."""
    contact_message_service = ContactUsService()

    try:
        db_contact_message = contact_message_service.create_contact_message(
            db, contact_message
        )
        return db_contact_message
    except Exception as e:  # noqa: F841
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        )
