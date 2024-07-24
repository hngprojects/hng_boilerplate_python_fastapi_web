# api/v1/routes/notificationroute.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.v1.services.notification_service import get_user_notifications
from api.v1.schemas.notificationschema import Notification as NotificationSchema
from api.utils.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("/current-user", response_model=List[NotificationSchema])
async def read_user_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id
    notifications = get_user_notifications(user_id, db)
    if notifications is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notifications not found")
    return {
        "message": "Notifications fetched successfully",
        "status_code": 200,
        "data": {
            "notifications": notifications
        }
    }
