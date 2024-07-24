"""
Superadmin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

# from fastapi.responses import JSONResponse
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from uuid import UUID

superadmin = APIRouter(prefix="", tags=["superadmin"])


@superadmin.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Session = Depends(get_db),
):
    # check if current user is an admin
    if not current_user.is_super_admin:
        raise HTTPException(
            detail="Access denied, Superadmin only",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    user = user_service.fetch(db=db, id=str(user_id))

    # check if the user_id points to a valid user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    # soft-delete the user
    user_service.delete(db=db, id=str(user_id))

    return success_response(
        status_code=status.HTTP_204_NO_CONTENT, message="user deleted successfully"
    )
