#!/usr/bin/env python3

from fastapi import APIRouter, Depends

from email_validator import validate_email, EmailNotValidError
from api.v1.models.user import WaitlistUser
from api.db.database import get_db

from api.utils.dependencies import get_current_admin
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.utils.json_response import JsonResponseDict
from api.utils.exceptions import CustomWaitlistException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Union


waitlist = APIRouter(prefix="/waitlist", tags=["Waitlist"])
db = next(get_db())

@waitlist.post(
    "/admin",
    responses={400: {"message": "Validation error"},
               403: {"message": "Forbidden"}},
)
def add_user_to_waitlist(
    item: WaitlistAddUserSchema,
    admin=Depends(get_current_admin)
):
    """
    Manually adds a user to the waitlist.
    This endpoint allows an admin to add a user to the waitlist.

    Parameters:
    - item: WaitlistAddUserSchema
        The details of the user to be added to the waitlist.
    - admin: User (Depends on get_current_admin)
        The current admin making the request. This is a dependency that provides the current admin context.

    Returns:
    - 201: User added successfully
    - 400: Validation error
    - 403: Forbidden
    """

    error_format: dict = {
        "message": "Invalid email format",
        "error": "Bad Request",
        "status_code": 400,
    }

    try:
        if len(item.full_name) == 0:
            error_format["message"] = "full_name field cannot be blank"
            raise CustomWaitlistException(status_code=400, detail=error_format)

        new_waitlist_user = WaitlistUser(email=item.email, full_name=item.full_name)
        db.add(new_waitlist_user)
        db.commit()
    except IntegrityError:
        error_format["message"] = "Email already added"
        raise CustomWaitlistException(status_code=400, detail=error_format)

    resp = {
        "message": "User added to waitlist successfully",
        "status_code": 201,
        "data": {"email": item.email, "full_name": item.full_name},
    }

    return JsonResponseDict(**resp)