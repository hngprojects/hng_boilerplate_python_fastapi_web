from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.data_privacy import data_privacy_service
from api.v1.schemas.data_privacy import DataPrivacySettingUpdate

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


@settings.patch("/data-privacy")
async def update_user_data_privacy_setting(
    schema: DataPrivacySettingUpdate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint to update a user's data privacy setting'
    """
    updated_settings = data_privacy_service.update(db=db, schema=schema, user=current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Data Privacy settings updated successfully",
        data=jsonable_encoder(updated_settings)
    )
