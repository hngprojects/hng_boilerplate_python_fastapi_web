from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.data_privacy import DataPrivacyUpdate
from api.v1.services.user import user_service
from api.v1.services.data_privacy import data_privacy_service

settings = APIRouter(prefix="/settings")


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


@settings.patch(
    "/data-privacy",
    summary="Update user data privacy",
    description="Updates the data privacy setting of the currently logged in user",
)
async def update_user_data_privacy_setting(
    data: DataPrivacyUpdate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    :param data: Data privacy update data
    :param current_user: The currently authenticated user
    :param db: Database session
    :return: Updated data privacy setting
    """

    data = data_privacy_service.update(db, data, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Data privacy setting updated successfully",
        data=jsonable_encoder(data),
    )
