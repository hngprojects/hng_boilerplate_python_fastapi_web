from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from api.v1.schemas.profile_settings import UserAndProfileUpdate
from api.v1.services.profile_settings import update_user_and_profile
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.user import user_service

settings = APIRouter(prefix="/api/v1", tags=["Profile-settings"])

@settings.patch("/users", status_code=status.HTTP_200_OK, response_model=success_response)
async def update_profile_settings(settings: UserAndProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """
    Update the authenticated user's profile. This endpoint allows partial updates.
    """

    db_user = update_user_and_profile(db=db, user_id=current_user["id"], user_profile=settings)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return success_response(
        status_code=201,
        message="Updated created successfully",
        data= jsonable_encoder(db_user)
    )
