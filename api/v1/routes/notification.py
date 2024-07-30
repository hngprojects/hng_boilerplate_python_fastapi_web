from fastapi import Depends, status, APIRouter, Path, HTTPException
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from api.db.database import get_db
from api.v1.services.user import user_service
from api.utils.email_service import send_mail
from api.v1.services.notification import notification_service
from api.v1.schemas.notification import NotificationRequest, ResponseModel


notification = APIRouter(prefix="/notifications", tags=["Notifications"])



@notification.post("/send", response_model=ResponseModel)
async def send_notification(request: NotificationRequest):
    """
    Endpoint to send an email notification.

    Args:
        request (NotificationRequest): The request object containing email, subject, and message.

    Returns:
        ResponseModel: The response model indicating the success of the operation.

    Raises:
        HTTPException: If there is an error in sending the email.
    """
    try:
        response = await notification_service.send_email(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@notification.patch(
    "/{id}",
    summary="Mark a notification as read",
    description="This endpoint marks a notification as `read`. User must be authenticated an must be the owner of a notification to mark it as `read`",
    status_code=status.HTTP_200_OK,
    response_model=success_response
)
def mark_notification_as_read(
    id: Annotated[str, Path()],
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    notification_service.mark_notification_as_read(
        notification_id=id, user=current_user, db=db
    )

    return success_response(status_code=200, message="Notifcation marked as read")


@notification.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    current_user = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
    ):

    notification_service.delete(
        notification_id,
        user=current_user,
        db=db
        )