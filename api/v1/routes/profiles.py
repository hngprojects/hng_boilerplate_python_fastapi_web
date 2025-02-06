from fastapi import (Depends, APIRouter,
                     Request,
                     status,  File,
                     UploadFile, HTTPException,
                     BackgroundTasks)
from sqlalchemy.orm import Session
from typing import Annotated
from PIL import Image
from io import BytesIO
from fastapi.responses import JSONResponse
import os

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.profile import (ProfileCreateUpdate,
                                    ProfileUpdateResponse,
                                    ProfileRecoveryEmailResponse,
                                    Token)
from api.db.database import get_db
from api.v1.schemas.user import DeactivateUserSchema
from api.v1.services.user import user_service
from api.v1.services.profile import profile_service


profile = APIRouter(prefix="/profile", tags=["Profiles"])


@profile.get(
    "/{user_id}", status_code=status.HTTP_200_OK, response_model=success_response
)
def get_current_user_profile(user_id: str,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(user_service.get_current_user)
):
    """Endpoint to get current user profile details"""

    profile = profile_service.fetch_by_user_id(db, user_id=user_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="User profile retrieved successfully",
        data=profile.to_dict(),
    )


@profile.post('/', status_code=status.HTTP_201_CREATED,
              response_model=success_response,
              include_in_schema=False)
def create_user_profile(
    schema: ProfileCreateUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to create user profile from the frontend'''

    user_profile = profile_service.create(db, schema=schema, user_id=current_user.id)

    response = success_response(
        status_code=status.HTTP_201_CREATED,
        message="User profile create successfully",
        data=user_profile.to_dict(),
    )

    return response


@profile.put("", status_code=status.HTTP_200_OK,
             response_model=ProfileUpdateResponse)
async def update_user_profile(
    schema: ProfileCreateUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    background_tasks: BackgroundTasks
):
    """Endpoint to update user profile"""
    return profile_service.update(db,
                                  schema,
                                  current_user,
                                  background_tasks)


@profile.post("/verify-recovery-email", status_code=status.HTTP_200_OK,
              response_model=ProfileRecoveryEmailResponse)
async def verify_recovery_email(
    token: Token,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(user_service.get_current_user)],
):
    return profile_service.update_recovery_email(current_user, db, token)

@profile.post("/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_account(
    request: Request,
    schema: DeactivateUserSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to deactivate a user account"""

    reactivation_link = user_service.deactivate_user(
        request=request, db=db, schema=schema, user=current_user
    )

    return success_response(
        status_code=200,
        message="User deactivation successful",
        data={"reactivation_link": reactivation_link},
    )


@profile.get("/reactivate", status_code=200)
async def reactivate_account(request: Request, db: Session = Depends(get_db)):
    """Endpoint to reactivate a user account"""

    # Get access token from query
    token = request.query_params.get("token")

    # reactivate user
    user_service.reactivate_user(db=db, token=token)

    return success_response(
        status_code=200,
        message="User reactivation successful",
    )

PROFILE_IMAGE_DIR = "static/profile_images"

@profile.post("/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    user_id = current_user.id

    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Only JPG and PNG are supported.")

    try:
        image = Image.open(BytesIO(await file.read()))
        image = image.resize((300, 300))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        file_name = f"{PROFILE_IMAGE_DIR}/{user_id}.jpg"
        os.makedirs(PROFILE_IMAGE_DIR, exist_ok=True)
        with open(file_name, "wb") as f:
            f.write(buffer.getbuffer())

        image_url = f"/static/profile_images/{user_id}.jpg"

        profile_service.update_user_avatar(db, user_id, image_url)

        return JSONResponse(status_code=200, content={"message": "Image uploaded successfully", "image_url": image_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")