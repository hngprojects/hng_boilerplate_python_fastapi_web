from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from api.db.database import get_db
from api.v1.models import User
from api.v1.schemas.contact import ContactMessageList
from api.v1.services.contact_us import ContactService
from api.v1.services.user import user_service

contact_us = APIRouter(prefix='/contact-us', tags=['ContactUs'])


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")


@contact_us.get('/messages/', response_model=ContactMessageList)
async def get_contact_messages(db: Session = Depends(get_db)):
    """
    Fetch all contact messages endpoint
    """
    request_user = Annotated[User, Depends(user_service.get_current_user)]
    # check if current user is an admin
    if not current_user.is_superadmin:
        raise HTTPException(
            detail="Access denied, Superadmin only",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    messages = ContactService.get_all_contact_messages(db)
    if not messages:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "No contact messages found.",
                "success": False,
                "status_code": 404
            }
        )
    return {"messages": messages}
