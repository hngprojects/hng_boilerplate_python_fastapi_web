from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.services.notification_settings import notification_settings_service
from api.v1.schemas.notification_settings import NotificationSettings

notification_setting = APIRouter(prefix='/notification-settings', tags=['Notification Settings'])


# Endpoint to update notification settings for a user
@notification_setting.patch('/{user_id}', status_code=status.HTTP_200_OK, response_model=NotificationSettings)
def update_notification_settings(user_id: str, settings: NotificationSettings, db: Session = Depends(get_db)):
    updated_settings = notification_settings_service.update(db=db, user_id=user_id, schema=settings)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="User notification retrieved successfully",
        data=updated_settings.to_dict()
    )