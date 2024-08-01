from fastapi import Depends, status, APIRouter, Path, HTTPException
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from api.db.database import get_db
from api.v1.services.user import user_service
from api.utils.email_service import send_mail
from api.v1.services.notification import notification_service
# from api.v1.schemas.notification import NotificationRead
from api.utils.dependencies import get_current_user
from api.v1.models.notifications import Notification
from api.v1.schemas.notification import ResponseModel, NotificationCreate


from api.v1.schemas.notification import NotificationCreate


notification = APIRouter(prefix="/notifications", tags=["Notifications"])


@notification.post("/send", response_model=ResponseModel)
async def create_notification(
    notification: NotificationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Create the notification
        created_notification = notification_service.create_notification(notification, user, db)
        
        # Convert the notification to a dictionary format if needed
        notification_data = {
            "id": created_notification.id,
            "user_id": created_notification.user_id,
            "title": created_notification.title,
            "message": created_notification.message,
            "created_at": created_notification.created_at
        }
        
        
        
        response = {
            "success": True,
            "status_code": 200,
            "message": "Notification created successfully",
            "data": notification_data
        }
        return response

    except Exception as e:
        # Construct an error response
        response = {
            "success": False,
            "status_code": 500,
            "message": f"An unexpected error occurred: {str(e)}",
            "error_details": str(e)
        }
        raise HTTPException(status_code=500, detail=str(response))




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
    "/{notification_id}",
    summary="Fetch a notification",
    description="This endpoint fetches a notification by id",
    status_code=status.HTTP_200_OK,
)
def get_notification_by_id(
    notification_id: str,
    db: Session = Depends(get_db),
):
    notification = notification_service.fetch_notification_by_id(
        notification_id=notification_id, db=db
    )
    return success_response(
        status_code=200, message="Notification fetched successfully", data=notification
    )
    
    
@notification.get(
    "/all",
    summary="Fetch all notifications",
    description="This endpoint fetches all notifications.",
    status_code=status.HTTP_200_OK,
)
def get_all_notifications(
    db: Session = Depends(get_db),
):
    notifications = notification_service.fetch_all_notifications(db=db)
    return success_response(
        status_code=200,
        message="All notifications fetched successfully",
        data=notifications,
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
