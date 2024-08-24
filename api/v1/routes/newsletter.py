from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from typing import Annotated
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.schemas.newsletter import (
    EmailSchema,
    EmailRetrieveSchema,
    SingleNewsletterResponse,
    UpdateNewsletter,
)
from api.db.database import get_db
from api.v1.services.newsletter import NewsletterService, Newsletter
from fastapi.encoders import jsonable_encoder
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.core.dependencies.email_sender import send_email

newsletter = APIRouter(prefix="/newsletters", tags=["Newsletter"])
news_sub = APIRouter(prefix="/newsletter-subscription", tags=["Newsletter"])
from api.utils.pagination import paginated_response


@news_sub.post("")
async def sub_newsletter(
    request: EmailSchema,
    db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
):
    """
    Newsletter subscription endpoint
    """

    # check for duplicate email
    is_subscribed = NewsletterService.check_existing_subscriber(db, request)

    if not is_subscribed:
        # Save user to the database
        NewsletterService.create(db, request)

        link = "https://anchor-python.teams.hng.tech/"

        # Send email in the background
        background_tasks.add_task(
            send_email,
            recipient=request.email,
            template_name="newsletter-subscription.html",
            subject="Thank You for Subscribing to HNG Boilerplate Newsletters",
            context={"link": link},
        )
        message = "Thank you for subscribing to our newsletter."
    else:
        message = "You have already subscribed to our newsletter. Thank you."

    return success_response(
        message=message,
        status_code=status.HTTP_200_OK,
    )


@newsletter.get(
    "/subscribers",
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


@newsletter.get(
    "/{id}", response_model=SingleNewsletterResponse, status_code=status.HTTP_200_OK
)
async def get_single_newsletter(id: str, db: Annotated[Session, Depends(get_db)]):
    """Retrieves a single newsletter."""
    newsletter = NewsletterService.fetch(db=db, id=id)
    return success_response(
        message="Successfully fetched newsletter", status_code=200, data=newsletter
    )


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


@newsletter.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
)
async def update_newsletter(
    id: str,
    schema: UpdateNewsletter,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    newsletter = NewsletterService.update(db, id, schema)
    return success_response(
        data=jsonable_encoder(newsletter),
        message="Successfully updated a newsletter",
        status_code=status.HTTP_200_OK,
    )


@newsletter.get("", status_code=200)
def get_all_newsletters(
    db: Session = Depends(get_db),
    page_size: Annotated[
        int, Query(ge=1, description="Number of products per page")
    ] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 0,
):
    """
    Retrieving all newsletters
    """

    return paginated_response(db=db, skip=page, limit=page_size, model=Newsletter)


@newsletter.post("/unsubscribe")
async def unsubscribe_newsletter(
    background_tasks: BackgroundTasks,
    request: EmailSchema,
    db: Session = Depends(get_db),
):
    """
    Newsletter unsubscription endpoint
    """
    NewsletterService.unsubscribe(db, request)
    background_tasks.add_task(
        send_email,
        recipient=request.email,
        template_name="unsubscribe.html",
        subject="Unsubscription from HNG Boilerplate Newsletter",
        context={},
    )
    return success_response(
        message="Unsubscribed successfully.",
        status_code=status.HTTP_200_OK,
    )
