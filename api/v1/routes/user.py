from typing import Annotated, Optional, Literal
from fastapi import Depends, APIRouter, Request, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.user import (
    AllUsersResponse, UserUpdate,
    AdminCreateUserResponse, AdminCreateUser
)
from api.db.database import get_db
from api.v1.services.user import user_service


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get('/delete', status_code=200)
async def delete_account(request: Request, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to delete a user account'''

    # Delete current user
    user_service.delete(db=db)

    return success_response(
        status_code=200,
        message='User deleted successfully',
    )

@user_router.patch("",status_code=status.HTTP_200_OK)
def update_current_user(
    current_user : Annotated[User , Depends(user_service.get_current_user)],
    schema : UserUpdate,
    db : Session = Depends(get_db),
):

    user = user_service.update(db=db, schema= schema, current_user=current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='User Updated Successfully',
        data= jsonable_encoder(
            user,
            exclude=['password', 'is_deleted', 'is_verified', 'updated_at', 'created_at', 'is_active']
        )
    )


@user_router.patch("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    user_id : str,
    current_user : Annotated[User , Depends(user_service.get_current_super_admin)],
    schema : UserUpdate,
    db : Session = Depends(get_db)
):
    user = user_service.update(db=db, schema=schema, id=user_id, current_user=current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='User Updated Successfully',
        data= jsonable_encoder(
            user,
            exclude=['password', 'is_superadmin', 'is_deleted', 'is_verified', 'updated_at', 'created_at', 'is_active']
        )
    )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
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

@user_router.get('', status_code=status.HTTP_200_OK, response_model=AllUsersResponse)
async def get_users(
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Annotated[Session, Depends(get_db)],
    page: int = 1, per_page: int = 10,
    is_active: Optional[bool] = Query(None),
    is_deleted: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    is_superadmin: Optional[bool] = Query(None)
):
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
        is_superadmin: boolean to filter users that are super admin
    Returns:
        UserData
    """
    query_params = {
        'is_active': is_active,
        'is_deleted': is_deleted,
        'is_verified': is_verified,
        'is_superadmin': is_superadmin,
    }
    return user_service.fetch_all(db, page, per_page, **query_params)

@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=AdminCreateUserResponse)
def admin_registers_user(
    user_request: AdminCreateUser,
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Session = Depends(get_db)
):
    '''
    Endpoint for an admin to register a user.
    Args:
        user_request: the body containing the user details to register
        current_user: The superadmin registering the user
        db: database Session object
    Returns:
        AdminCreateUserResponse: The full details of the newly created user
    '''
    return user_service.super_admin_create_user(db, user_request)
    

@user_router.get('/{role_id}/roles', status_code=status.HTTP_200_OK)
async def get_users_by_role(
    role_id: Literal["admin", "user", "guest", "owner"], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get all users by role'''
    users = user_service.get_users_by_role(db, role_id, current_user)

    return success_response(
        status_code=200,
        message='Users retrieved successfully',
        data=jsonable_encoder(users)
    )


@user_router.get('/organisations', status_code=200, response_model=success_response)
def get_current_user_organisations(
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get all current user organisations'''

    return success_response(
        status_code=200,
        message='Organisations fetched successfully',
        data=jsonable_encoder(current_user.organisations)
    )


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id : str,
    db : Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    
    user = user_service.get_user_by_id(db=db, id=user_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='User retrieved successfully',
        data = jsonable_encoder(
            user, 
            exclude=['password', 'is_superadmin', 'is_deleted', 'is_verified', 'updated_at', 'created_at', 'is_active']
        )
    )
