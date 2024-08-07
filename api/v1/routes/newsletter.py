from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.schemas.newsletter import EmailSchema, EmailRetrieveSchema, SingleNewsletterResponse
from api.db.database import get_db
from api.v1.services.newsletter import NewsletterService
from fastapi.encoders import jsonable_encoder
from api.v1.models.user import User
from api.v1.services.user import user_service

newsletter = APIRouter(prefix="/pages/newsletters", tags=["Newsletter"])


@newsletter.post("/")
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
        status_code=status.HTTP_201_CREATED,
    )


@newsletter.get(
    "/",
    response_model=success_response,
    status_code=200,
)
def retrieve_subscribers(
    db: Session = Depends(get_db),
    admin: User = Depends(user_service.get_current_super_admin),
):
    """
    Retrieve all newsletter subscription from database
    """

    subscriptions = NewsletterService.fetch_all(db)
    subs_filtered = list(
        map(lambda x: EmailRetrieveSchema.model_validate(x), subscriptions)
    )

    if len(subs_filtered) == 0:
        subs_filtered = [{}]

    return success_response(
        message="Subscriptions retrieved successfully",
        status_code=200,
        data=jsonable_encoder(subs_filtered),
    )

@newsletter.get('/{id}', response_model=SingleNewsletterResponse, status_code=status.HTTP_200_OK)
async def get_single_newsletter(
    id: str,
    db: Annotated[Session, Depends(get_db)],
    ):
    """Retrieves a single newsletter.

    Args:
        id: The id of the job for the newsletter
        db: database Session object

    Returns:
        SingleNewslettersResponse: response on success
    """
    newsletterservice = NewsletterService()
    return newsletterservice.fetch(news_id=id, db=db)

@newsletter.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete single newsletter",
    description="Endpoint to delete a single newsletter by ID",
)
def delete_newsletter(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to delete a newsletter"""
    NewsletterService.delete(db=db, id=id)

@newsletter.post('/newsletters/unsubscribe')
async def unsubscribe_newsletter(request: EmailSchema, db: Session = Depends(get_db)):
    """
    Newsletter unsubscription endpoint
    """
    NewsletterService.unsubscribe(db, request)
    return success_response(
        message="Unsubscribed successfully.",
        status_code=status.HTTP_200_OK,
    )