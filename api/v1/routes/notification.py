from fastapi import Depends, status, APIRouter, Path, HTTPException
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.notification import notification_service
# from api.v1.schemas.notification import NotificationRead
from api.v1.models.notifications import Notification


notification = APIRouter(prefix="/notifications", tags=["Notifications"])


@notification.patch(
    "/{id}",
    summary="Mark a notification as read",
    description="This endpoint marks a notification as `read`. User must be authenticated an must be the owner of a notification to mark it as `read`",
    status_code=status.HTTP_200_OK,
    response_model=success_response,
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


@notification.get("/current-user")
def get_current_user_notifications(
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    data = notification_service.get_current_user_notifications(current_user, db)
    return success_response(status_code=200, message="All notifications", data=data)


@notification.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    current_user=Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):

    notification_service.delete(notification_id, user=current_user, db=db)


# @notification.get("/{notification_id}", status_code=status.HTTP_200_OK)
# def get_notification(
#     notification_id: str,
#     current_user: User = Depends(user_service.get_current_user),
#     db: Session = Depends(get_db)
# ):
#     notification = notification_service.fetch(
#         notification_id=notification_id,
#         user=current_user,
#         db=db
#     )
#     return {"message": "Notification fetched successfully", "status_code": 200, "success": True, "data": notification}
