from fastapi import Depends, status, APIRouter, Path
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from api.db.database import get_db
from api.v1.schemas.notification_settings import NotificationSettingsBase
from api.v1.services.user import user_service
from api.v1.services.notification_settings import notification_setting_service
from api.v1.models.notifications import NotificationSetting


notification_setting = APIRouter(prefix="/settings/notification-settings", tags=["Notification Settings"])

@notification_setting.get('', response_model=success_response, status_code=200)
def get_user_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get current user notification preferences settings'''

    settings = notification_setting_service.fetch_by_user_id(db=db, user_id=current_user.id)

    return success_response(
        status_code=200,
        message="Notification preferences retrieved successfully",
        data=jsonable_encoder(settings)
    )

@notification_setting.post('', response_model=success_response, status_code=200)
def create_user_notification_settings(
    schema: NotificationSettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to create new notification settings for the current user'''

    settings = notification_setting_service.update(
        db=db, 
        user_id=current_user.id,
        schema=schema
    )

    return success_response(
        status_code=201,
        message="Notification settings created successfully",
        data=jsonable_encoder(settings)
    )


@notification_setting.patch('', response_model=success_response, status_code=200)
def update_user_notification_settings(
    schema: NotificationSettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to update current user notification preferences settings'''

    settings = notification_setting_service.update(
        db=db, 
        user_id=current_user.id,
        schema=schema
    )

    return success_response(
        status_code=200,
        message="Notification preferences updated successfully",
        data=jsonable_encoder(settings)
    )
