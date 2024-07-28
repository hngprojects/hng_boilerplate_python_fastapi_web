from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
import logging

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.profile import ProfileCreateUpdate
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.profile import profile_service


profile = APIRouter(prefix="/profile", tags=["Profiles"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@profile.get(
    "/current-user", status_code=status.HTTP_200_OK, 
    response_model=success_response
)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get current user profile details"""

    profile = profile_service.fetch_by_user_id(db, user_id=current_user.id)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile create successfully",
        data=profile.to_dict(),
    )


@profile.post("/", status_code=status.HTTP_201_CREATED,
              response_model=success_response)
def create_user_profile(
    schema: ProfileCreateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to create user profile from the frontend"""

    user_profile = profile_service.create(db, schema=schema, 
                                          user_id=current_user.id)

    response = success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile create successfully",
        data=user_profile.to_dict(),
    )


@profile.patch("/", status_code=status.HTTP_200_OK, 
               response_model=success_response)
def update_user_profile(
    schema: ProfileCreateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to update user profile"""
    logger.debug(f"Updating profile for user: {current_user}")
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    else:
        logger.debug(f"Current user ID: {current_user.id}")
    updated_profile = profile_service.update(db, schema=schema, 
                                             user_id=current_user.id)

    response = success_response(
        status_code=status.HTTP_200_OK,
        message="User profile updated successfully",
        data=updated_profile.to_dict(),
    )

    return response
