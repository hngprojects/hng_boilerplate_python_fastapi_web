#!/usr/bin/env python3

from fastapi import APIRouter, Depends

from api.v1.models.waitlist import Waitlist
from api.db.database import get_db

from api.utils.dependencies import get_super_admin
from api.v1.schemas.waitlist import WaitlistAddUserSchema
from api.utils.json_response import JsonResponseDict
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from api.v1.services.waitlist import waitlist_service

waitlist = APIRouter(prefix="/waitlist", tags=["Waitlist"])

@waitlist.post(
    "/admin",
    responses={400: {"message": "Validation error"},
               403: {"message": "Forbidden"}},
)
def add_user_to_waitlist(
    item: WaitlistAddUserSchema,
    admin=Depends(get_super_admin),
    db: Session = Depends(get_db)

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
        
        if obj:= waitlist_service.fetch_by_email(db, item.email):
            print(obj)
            raise IntegrityError("Duplicate entry", {}, None)
        print(f'Her!!{obj}')

        new_waitlist_user = waitlist_service.create(db, item)
    except IntegrityError:
        detail = "Email already added"
        raise HTTPException(status_code=400, detail=detail)

    resp = {
        "message": "User added to waitlist successfully",
        "status_code": 201,
        "data": {"email": item.email, "full_name": item.full_name},
    }

    return JsonResponseDict(**resp)