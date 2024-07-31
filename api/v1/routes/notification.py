from fastapi import Depends, status, APIRouter, Path, HTTPException
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.notification import notification_service

from api.v1.schemas.notification import NotificationCreate


notification = APIRouter(prefix="/notifications", tags=["Notifications"])


@notification.post(
    "/send",
    summary="Send a notification",
    description="This endpoint sends a notification to a user. User must be authenticated",
    status_code=status.HTTP_201_CREATED,
)
def send_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
):
    notification = notification_service.send_notification(
        user_id=notification_data.user_id,
        title=notification_data.title,
        message=notification_data.message,
        db=db,
    )
    return success_response(
        status_code=201, message="Notification sent successfully", data=notification
    )


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

    return success_response(status_code=200, message="Notification marked as read")


@notification.get("/current-user")
def get_current_user_notifications(
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    data = notification_service.get_current_user_notifications(current_user, db)
    return success_response(status_code=200, message="All notifications", data=data)


@notification.get(
    "/all",
    summary="Fetch all notifications",
    description="This endpoint fetches all notifications. User must be authenticated as a `super_admin` to be able fetch it",
    status_code=status.HTTP_200_OK,
)
def get_all_notifications(
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view all notifications",
        )

    notifications = notification_service.fetch_all_notifications(db=db)
    return success_response(
        status_code=200,
        message="All notifications fetched successfully",
        data=notifications,
    )


@notification.get(
    "/{notification_id}",
    summary="Fetch a notification",
    description="This endpoint fetches a notification by id. User must be authenticated as an `super_admin` to be able fetch it",
    status_code=status.HTTP_200_OK,
)
def get_notification_by_super_admin(
    notification_id: str,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view this notification",
        )

    notification = notification_service.fetch_notification_by_super_admin(
        notification_id=notification_id, db=db
    )
    return success_response(
        status_code=200, message="Notification fetched successfully", data=notification
    )


@notification.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: str,
    current_user=Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    notification_service.delete_notification(notification_id, current_user, db)
    return success_response(
        status_code=204, message="Notification deleted successfully"
    )
