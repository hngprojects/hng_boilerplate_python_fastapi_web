#!/usr/bin/env python3

from api.utils.dependencies import get_super_admin
from api.utils.success_response import success_response
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.utils.json_response import JsonResponseDict
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, HTTPException, Depends, Request
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


@waitlist.post("/", response_model=success_response, status_code=201)
async def waitlist_signup(
    request: Request, user: WaitlistAddUserSchema, db: Session = Depends(get_db)
):
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

    try:
        # await send_confirmation_email(user.email, user.full_name)
        logger.info(f"Confirmation email sent successfully to {user.email}")
    except HTTPException as e:
        logger.error(f"Failed to send confirmation email: {e.detail}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to send confirmation email",
                "success": False,
                "status_code": 500,
            },
        )

    logger.info(f"User signed up successfully: {user.email}")
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
    Manually adds a user to the waitlist.
    This endpoint allows an admin to add a user to the waitlist.

    Parameters:
    - item: WaitlistAddUserSchema
        The details of the user to be added to the waitlist.
    - admin: User (Depends on get_super_admin)
        The current admin making the request. This is a dependency that provides the current admin context.

    Returns:
    - 201: User added successfully
    - 400: Validation error
    - 403: Forbidden
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
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_super_admin)
):
    waitlist_users = waitlist_service.fetch_all(db)
    emails = [{"email": user.email, "full_name": user.full_name} for user in waitlist_users]

    return success_response(
        message="Waitlist retrieved successfully",
        status_code=200,
        data=emails
    )
