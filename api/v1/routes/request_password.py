import json
from fastapi import (APIRouter, Depends, status,
                     HTTPException, BackgroundTasks)
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Annotated
from api.v1.schemas.request_password_reset import (RequestEmail,
                                                   ResetPasswordRequest,
                                                   ResetPasswordResponse,
                                                   ResetPasswordSuccesful)
from datetime import timedelta
from api.db.database import get_db
from api.v1.services.request_pwd import reset_password_service
import logging
from api.core.dependencies.email_sender import send_email


pwd_reset = APIRouter(prefix="/auth", tags=["Authentication"])




# generate password reset link
@pwd_reset.post("/forgot-password", status_code=status.HTTP_200_OK,
                response_model=ResetPasswordResponse)
async def request_reset_link(
    reset_email: RequestEmail,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Generates a link for resetting password for a user.
        Args:
            reset_email: The request body containing the data
            background_tasks: The Background task method.
            db: the database Session object.
        Retuns:
            Response: response containing a successful message.
        Raises:
            HTTPException: If anything goes wrong
    """
    user = reset_password_service.fetch(reset_email.email, db)
    reset_token = reset_password_service.create(user, db)
   
    link = f"https://anchor-python.teams.hng.tech/reset-password?token={reset_token}"
   
    try:
        background_tasks.add_task(
            send_email,
            recipient=user.email,
            template_name="reset-password.html",
            subject="Password Reset",
            context={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "link": link
            }
        )
       
        return ResetPasswordResponse(
            message="Reset password link successfully sent to user",
            status_code=status.HTTP_200_OK
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # change the password
@pwd_reset.patch("/reset-password", status_code=status.HTTP_201_CREATED,
                 response_model=ResetPasswordSuccesful)
async def reset_password(
    reset_password_data: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Verifies and resets password for a user.
        Args:
            reset_password_data: The request body containing the data
            db: the database Session object.
        Retuns:
            Response: response containing user information and access token
        Raises:
            HTTPException: If anything goes wrong
    """
    response_data, refresh_token = reset_password_service.update(reset_password_data,
                                                                 db)
    response = Response(content=json.dumps(response_data.model_dump()),
                        status_code=status.HTTP_201_CREATED,
                        media_type="application/json")
   
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )
    return response
