#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse

from api.v1.models.org import Organization
from api.v1.models.invitation import Invitation
from api.db.database import get_db

from api.utils.dependencies import get_current_user
from api.v1.schemas.auth import UserBase
from api.v1.schemas.invitation import DeactivateInviteBody

db = next(get_db())

class CustomInviteDeactivateException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.errors = detail.get("errors")
        self.status_code = detail.get("status_code")

async def custom_invite_deactivate_exception_handler(request: Request, exc: CustomInviteDeactivateException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "errors": exc.errors,
            "status_code": exc.status_code
        }
    )






router = APIRouter()
@router.patch(
    "/api/v1/invite/deactivate",
    responses={400: {"message": "Validation error"},
               403: {"message": "Forbidden"}}
)
async def deactivate_invite_link(
    item: DeactivateInviteBody, user: UserBase = Depends(get_current_user)
):

    link = item.invitation_link
    invitation = db.query(Invitation).where(Invitation.id == link).first()
    error_format: dict = {
        "message": "Validation error",
        "errors": [{"field": "", "message": ""}],
        "status_code": 400
    }

    if not invitation or not invitation.is_valid:
        error_format['errors'][0]['field'] = "invitation_link"
        error_format['errors'][0]['message'] = "Invalid or expired invitation link"
        raise CustomInviteDeactivateException(
            status_code=400,
            detail= error_format
        )

    org_id = invitation.organization_id
    org = db.query(Organization).where(Organization.id == org_id).first()
    if org is None:
        error_format['errors'][0]['field'] = "organization"
        error_format['errors'][0]['message'] = "Organization not found"
        raise CustomInviteDeactivateException(
            status_code=400,
            detail=error_format,
        )
    if user.id != invitation.user_id:
        error_format['message'] = "Forbidden"
        error_format['errors'][0]['field'] = "authorization"
        error_format['errors'][0]['message'] = "User is not authorized to deactivate this invitation link"
        error_format['status_code'] = 403
        raise CustomInviteDeactivateException(
            status_code=403,
            detail=error_format
        )
    invitation.is_valid = False
    db.commit()

    return {"message": "Invitation link has been deactivated", "status_code": 200}