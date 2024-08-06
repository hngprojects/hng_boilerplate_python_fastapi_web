from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.data_privacy import data_privacy_service
from api.v1.schemas.notification_settings import NotificationSettingsBase
from api.v1.services.notification_settings import notification_setting_service


settings = APIRouter(prefix="/settings", tags=["settings"])


@settings.get("/data-privacy")
async def get_user_data_privacy_setting(
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to get a user's data privacy setting
    """

    data = data_privacy_service.fetch(db, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Data privacy setting fetched successfully",
        data=jsonable_encoder(data),
    )


@settings.get(
    "/notification-settings", response_model=success_response, status_code=200
)
def get_user_notification_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get current user notification preferences settings"""

    settings = notification_setting_service.fetch_by_user_id(
        db=db, user_id=current_user.id
    )

    return success_response(
        status_code=200,
        message="Notification preferences retrieved successfully",
        data=jsonable_encoder(settings),
    )


@settings.post(
    "/notification-settings", response_model=success_response, status_code=200
)
def create_user_notification_settings(
    schema: NotificationSettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to create new notification settings for the current user"""

    settings = notification_setting_service.update(
        db=db, user_id=current_user.id, schema=schema
    )

    return success_response(
        status_code=201,
        message="Notification settings created successfully",
        data=jsonable_encoder(settings),
    )


@settings.patch(
    "/notification-settings", response_model=success_response, status_code=200
)
def update_user_notification_settings(
    schema: NotificationSettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to update current user notification preferences settings"""

    settings = notification_setting_service.update(
        db=db, user_id=current_user.id, schema=schema
    )

    return success_response(
        status_code=200,
        message="Notification preferences updated successfully",
        data=jsonable_encoder(settings),
    )
