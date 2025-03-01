<<<<<<< Updated upstream
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
=======
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
>>>>>>> Stashed changes
from sqlalchemy.orm import Session

from api.core.responses import SUCCESS
<<<<<<< Updated upstream
from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models import *
from api.v1.schemas.squeeze import CreateSqueeze, FilterSqueeze, UpdateSqueeze
from api.v1.services.squeeze import squeeze_service
from api.v1.services.user import user_service
=======
from api.v1.schemas.squeeze import SuccessResponseSchema
from api.v1.services.squeeze import squeeze_service
from api.v1.schemas.squeeze import CreateSqueeze, FilterSqueeze
from api.v1.services.user import user_service
from api.v1.models.user import User
>>>>>>> Stashed changes

squeeze = APIRouter(prefix="/squeeze", tags=["Squeeze Page"])


@squeeze.post("", response_model=SuccessResponseSchema, status_code=201)
def create_squeeze(
    background_tasks: BackgroundTasks,
    data: CreateSqueeze,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Create a squeeze page"""
    user = user_service.fetch_by_email(db, data.email)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found!")
    data.user_id = user.id
    data.full_name = f"{user.first_name} {user.last_name}"
    new_squeeze = squeeze_service.create(background_tasks, db, data)
    return SuccessResponseSchema(status=status.HTTP_201_CREATED, message=SUCCESS, data=new_squeeze.to_dict())


@squeeze.get("", response_model=SuccessResponseSchema, status_code=200)
def get_all_squeeze(
    filter: FilterSqueeze = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Get all squeeze pages"""
    squeeze_pages = squeeze_service.fetch_all(db, filter)
    return SuccessResponseSchema(status.HTTP_200_OK, SUCCESS, squeeze_pages)


@squeeze.get("/{squeeze_id}", response_model=SuccessResponseSchema, status_code=200)
def get_squeeze(
    squeeze_id: str,
    filter: FilterSqueeze = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Get a squeeze page"""
    squeeze_page = squeeze_service.fetch(db, squeeze_id, filter)
    if not squeeze_page:
        return SuccessResponseSchema(status=status.HTTP_404_NOT_FOUND, detail="Squeeze page not found!")
    return SuccessResponseSchema(status.HTTP_200_OK, SUCCESS, squeeze_page)


@squeeze.delete("/{squeeze_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_squeeze(
    squeeze_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Delete a squeeze page"""
    squeeze_service.delete(db, squeeze_id)


<<<<<<< Updated upstream
@squeeze.put(
    "/{squeeze_id}", response_model=success_response, status_code=status.HTTP_200_OK
)
def update_squeeze(
    squeeze_id: str,
    data: UpdateSqueeze,
    db: Session = Depends(get_db),
    authorized_user: User = Depends(user_service.get_current_super_admin),
):
    """Update a squeeze page"""

    if not authorized_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")

    updated_squeeze = squeeze_service.update(db, squeeze_id, data)
    return success_response(
        status.HTTP_200_OK,
        "Squeeze page updated successfully",
        updated_squeeze.to_dict(),
    )
=======

>>>>>>> Stashed changes
