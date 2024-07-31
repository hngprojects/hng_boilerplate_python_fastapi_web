from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.profile import ProfileCreateUpdate, UserAndProfileUpdate
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.profile import profile_service, update_user_and_profile
from api.utils.success_response import success_response


profile = APIRouter(prefix='/profile', tags=['Profiles'])

@profile.get('/current-user', status_code=status.HTTP_200_OK, response_model=success_response)
def get_current_user_profile(db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to get current user profile details'''

    profile = profile_service.fetch_by_user_id(db,user_id=current_user.id)
    
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile create successfully", 
        data=profile.to_dict()
    )

@profile.post('/', status_code=status.HTTP_201_CREATED, response_model=success_response)
def create_user_profile(schema: ProfileCreateUpdate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to create user profile from the frontend'''

    user_profile = profile_service.create(db, schema=schema, user_id=current_user.id)
    
    response = success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile create successfully", 
        data=user_profile.to_dict()
    )

    return response


settings = APIRouter(prefix="/api/v1/users", tags=["Profile-settings"])

@settings.patch("/settings", status_code=status.HTTP_200_OK, response_model=success_response)
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
