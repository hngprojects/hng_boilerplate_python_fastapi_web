from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import logging

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.profile import ProfileBase, ProfileCreateUpdate
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.profile import profile_service
from api.utils.dependencies import get_current_user

profile = APIRouter(prefix="/profile", tags=["Profiles"])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@profile.get(
    "/current-user", status_code=status.HTTP_200_OK, response_model=ProfileBase
)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get current user profile details"""
    user_profile = profile_service.fetch_by_user_id(db, user_id=current_user.id)
    return jsonable_encoder(user_profile.to_dict())

@profile.post("/", status_code=status.HTTP_201_CREATED, response_model=ProfileBase)
def create_user_profile(
    schema: ProfileCreateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to create user profile from the frontend"""

    user_profile = profile_service.create(db, schema=schema, user_id=current_user.id)

    response = success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile created successfully",
        data=jsonable_encoder(user_profile.to_dict()),
    )

    return response

@profile.patch("/", status_code=status.HTTP_200_OK, response_model=ProfileBase)
def update_user_profile(
    schema: ProfileCreateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Endpoint to update user profile from the frontend"""
    logger.debug(f"Updating profile for user: {current_user}")
    if current_user is None:
        raise HTTPException(status_code=401, detail="User not authenticated")
    else:
        logger.debug(f"Current user ID: {current_user.id}")
    updated_profile = profile_service.update(
        db, schema=schema, user_id=current_user.id
    )
    return updated_profile