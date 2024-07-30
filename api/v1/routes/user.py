from typing import Annotated, Optional
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.user import (
    DeactivateUserSchema,
    ChangePasswordSchema,
    ChangePwdRet, AllUsersResponse
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


@user.get('/delete', status_code=200)
async def delete_account(request: Request, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to delete a user account'''

    # Delete current user
    user_service.delete(db=db)

    return success_response(
        status_code=200,
        message='User deleted successfully',
    )


@user.patch("/me/password", status_code=200)
async def change_password(
    schema: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    """Endpoint to change the user's password"""

    user_service.change_password(schema.old_password, schema.new_password, user, db)

    return success_response(
        status_code=200,
        message='Password changed successfully'
    )

@user.get(path="/{user_id}", status_code=status.HTTP_200_OK)
def get_user(
    user_id : str,
    current_user : Annotated[User , Depends(user_service.get_current_user)],
    db : Session = Depends(get_db)
):
    
    user = user_service.fetch(db=db, id=user_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='User retrieved successfully',
        data = jsonable_encoder(
            user, 
            exclude=['password', 'is_super_admin', 'is_deleted', 'is_verified', 'updated_at', 'created_at', 'is_active']
        )
    )

@user.delete(path="/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Session = Depends(get_db),
):
    """Endpoint for user deletion (soft-delete)"""

    """

    Args:
        user_id (str): User ID
        current_user (User): Current logged in user
        db (Session, optional): Database Session. Defaults to Depends(get_db).

    Raises:
        HTTPException: 403 FORBIDDEN (Current user is not a super admin)
        HTTPException: 404 NOT FOUND (User to be deleted cannot be found)
    """

    user = user_service.fetch(db=db, id=user_id)

    # soft-delete the user
    user_service.delete(db=db, id=user_id)

@user.get('/', status_code=status.HTTP_200_OK, response_model=AllUsersResponse)
async def get_users(current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
                    db: Annotated[Session, Depends(get_db)],
                    page: int = 1, per_page: int = 10,
                    is_active: Optional[bool] = Query(None),
                    is_deleted: Optional[bool] = Query(None),
                    is_verified: Optional[bool] = Query(None),
                    is_super_admin: Optional[bool] = Query(None)):
    """
    Retrieves all users.
    Args:
        current_user: The current user(admin) making the request
        db: database Session object
        page: the page number
        per_page: the maximum size of users for each page
        is_active: boolean to filter active users
        is_deleted: boolean to filter deleted users
        is_verified: boolean to filter verified users
        is_super_admin: boolean to filter users that are super admin
    Returns:
        UserData
    """
    query_params = {
        'is_active': is_active,
        'is_deleted': is_deleted,
        'is_verified': is_verified,
        'is_super_admin': is_super_admin,
    }
    return user_service.fetch_all(db, page, per_page, **query_params)

