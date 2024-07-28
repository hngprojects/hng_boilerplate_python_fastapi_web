from fastapi import Depends, APIRouter, Request, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.user import (
    DeactivateUserSchema,
    ChangePasswordSchema,
    ChangePwdRet,
)
from api.db.database import get_db
from api.v1.services.user import user_service


user = APIRouter(prefix="/users", tags=["Users"])


@user.get("/me", status_code=status.HTTP_200_OK, response_model=success_response)
def get_current_user_details(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get current user details"""

    return success_response(
        status_code=200,
        message="User details retrieved successfully",
        data=jsonable_encoder(
            current_user,
            exclude=[
                "password",
                "is_super_admin",
                "is_deleted",
                "is_verified",
                "updated_at",
            ],
        ),
    )


@user.post("/deactivation", status_code=status.HTTP_200_OK)
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


@user.get("/reactivation", status_code=200)
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


# @user.get('/current-user/delete', status_code=200)
# async def delete_account(request: Request, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
#     '''Endpoint to delete a user account'''

#     # Delete current user
#     user_service.delete(db=db)

#     return success_response(
#         status_code=200,
#         message='User deleted successfully',
#     )


@user.patch("/me/password", status_code=200, response_model=ChangePwdRet)
async def change_password(
    schema: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    """Endpoint to change the user's password"""

    user_service.change_password(schema.old_password, schema.new_password, user, db)

    return success_response(status_code=200, message="Password changed successfully")
