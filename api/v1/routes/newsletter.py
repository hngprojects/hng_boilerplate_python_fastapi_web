from fastapi import (
    APIRouter,
    Depends,
    status
    )
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.schemas.newsletter import EmailSchema
from api.db.database import get_db
from api.v1.services.newsletter import NewsletterService


newsletter = APIRouter(tags=['Newsletter'])

@newsletter.post('/newsletters')
async def sub_newsletter(request: EmailSchema, db: Session = Depends(get_db)):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    NewsletterService.check_existing_subscriber(db, request)

    # Save user to the database
    NewsletterService.create(db, request)

    return success_response(
        message="Thank you for subscribing to our newsletter.",
        status_code=status.HTTP_201_CREATED
    )
