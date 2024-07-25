"""
Superadmin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.schemas.user import UserCreate,UserBase
# from uuid import UUID

superadmin = APIRouter(prefix="/superadmin", tags=["superadmin"])

db_dependency = Annotated[Session , Depends(get_db)]



@superadmin.post(path='/register', status_code=status.HTTP_201_CREATED)
def register_admin(user : UserCreate , db : db_dependency):
    """The Endpoint created is for the creation of super admins 
    """
    user_created = user_service.create_admin(db=db, schema=user)
    return success_response(
        status_code=201,
        message= 'User Created Successfully',
        data=user_created.to_dict()
    )

  
@superadmin.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Session = Depends(get_db),
):
    """Endpoint for user deletion (soft-delete)"""

    """

    Args:
        user_id (UUID): User ID
        current_user (User): Current logged in user
        db (Session, optional): Database Session. Defaults to Depends(get_db).

    Raises:
        HTTPException: 403 FORBIDDEN (Current user is not a super admin)
        HTTPException: 404 NOT FOUND (User to be deleted cannot be found)

    Returns:
        JSONResponse: 204 NO CONTENT (successful user deletion)
    """

    user = user_service.fetch(db=db, id=user_id)

    # check if the user_id points to a valid user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    # soft-delete the user
    user_service.delete(db=db, id=user_id)

    return success_response(
        status_code=status.HTTP_200_OK, message="user deleted successfully"
    )