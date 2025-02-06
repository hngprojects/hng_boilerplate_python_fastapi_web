#!/usr/bin/env python3

from api.utils.dependencies import get_super_admin
from api.utils.success_response import success_response
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.utils.json_response import JsonResponseDict
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from api.core.dependencies.email_sender import send_email
from fastapi import APIRouter, HTTPException, Depends, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.v1.services.waitlist_email import (
    send_confirmation_email,
    add_user_to_waitlist,
    find_existing_user,
)
from api.utils.logger import logger
from api.db.database import get_db
from api.v1.services.waitlist import waitlist_service

waitlist = APIRouter(prefix="/waitlist", tags=["Waitlist"])

def process_waitlist_signup(user: WaitlistAddUserSchema, db: Session):
    """
    Process a waitlist signup request.

    Args:
    - user (WaitlistAddUserSchema): The user details to be added to the waitlist.
    - db (Session): The database session.

    Returns:
    - db_user: The added user object.

    Raises:
    - HTTPException: If the full name is not provided or if the email is already registered.
    """
    if not user.full_name:
        logger.error("Full name is required")
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Full name is required",
                "success": False,
                "status_code": 422,
            },
        )

    existing_user = find_existing_user(db, user.email)
    if existing_user:
        logger.error(f"Email already registered: {user.email}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Email already registered",
                "success": False,
                "status_code": 400,
            },
        )

    db_user = add_user_to_waitlist(db, user.email, user.full_name)
    return db_user

@waitlist.post("/", response_model=success_response, status_code=201)
async def waitlist_signup(
    background_tasks: BackgroundTasks,
    request: Request,
    user: WaitlistAddUserSchema,
    db: Session = Depends(get_db)
):
    """
    Add a user to the waitlist.

    Args:
    - user (WaitlistAddUserSchema): The user details to be added to the waitlist.

    Returns:
    - success_response: A success response with a message and status code.

    Example:
    ```
    curl -X POST \
      http://localhost:8000/waitlist/ \
      -H 'Content-Type: application/json' \
      -d '{"email": "user@example.com", "full_name": "John Doe"}'
    ```
    """
     
    db_user = process_waitlist_signup(user, db)
    if db_user:
        cta_link = 'https://anchor-python.teams.hng.tech/about-us'
        # Send email in the background
        background_tasks.add_task(
            send_email, 
            recipient=user.email,
            template_name='waitlists.html',
            subject='Welcome to HNG Waitlist',
            context={
                'name': user.full_name,
                'cta_link': cta_link
            }
        )
    return success_response(message="You are all signed up!", status_code=201)


@waitlist.post(
    "/admin",
    responses={400: {"message": "Validation error"}, 403: {"message": "Forbidden"}},
)
def admin_add_user_to_waitlist(
    item: WaitlistAddUserSchema,
    admin=Depends(get_super_admin),
    db: Session = Depends(get_db),
):
    """
    Manually add a user to the waitlist as an admin.

    Args:
    - item (WaitlistAddUserSchema): The user details to be added to the waitlist.
    - admin (User): The current admin making the request.

    Returns:
    - success_response: A success response with a message and status code.

    Raises:
    - HTTPException: If the full name is not provided or if the email is already registered.

    Example:
    ```
    curl -X POST \
      http://localhost:8000/waitlist/admin \
      -H 'Content-Type: application/json' \
      -d '{"email": "user@example.com", "full_name": "John Doe"}'
    ```
    """

    try:
        if len(item.full_name) == 0:
            detail = "full_name field cannot be blank"
            raise HTTPException(status_code=400, detail=detail)

        if obj := find_existing_user(db, item.email):
            raise IntegrityError("Duplicate entry", {}, None)

        new_waitlist_user = add_user_to_waitlist(db, **item.model_dump())
    except IntegrityError:
        detail = "Email already added"
        raise HTTPException(status_code=400, detail=detail)

    return success_response(
        message="User added to waitlist successfully",
        status_code=201,
        data={"email": item.email, "full_name": item.full_name},
    )

    return JsonResponseDict(**resp)


@waitlist.get("/users", response_model=success_response, status_code=200)
async def get_all_waitlist_emails(
    request: Request, db: Session = Depends(get_db), admin=Depends(get_super_admin)
):
    waitlist_users = waitlist_service.fetch_all(db)
    emails = [
        {"email": user.email, "full_name": user.full_name} for user in waitlist_users
    ]

    return success_response(
        message="Waitlist retrieved successfully", status_code=200, data=emails
    )


@waitlist.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_waitlist_by_email(
    id: str, admin=Depends(get_super_admin), db: Session = Depends(get_db)
):
    """Remove a waitlisted user with the id"""

    waitlist_service.delete(db, id)
