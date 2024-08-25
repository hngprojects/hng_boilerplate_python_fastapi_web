from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.core.responses import SUCCESS
from api.utils.success_response import success_response
from api.v1.services.squeeze import squeeze_service
from api.v1.schemas.squeeze import CreateSqueeze, FilterSqueeze
from api.v1.services.user import user_service
from api.v1.models import *

squeeze = APIRouter(prefix="/squeeze", tags=["Squeeze Page"])


@squeeze.post("", response_model=success_response, status_code=201)
def create_squeeze(
    background_tasks: BackgroundTasks,
    data: CreateSqueeze,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Create a squeeze page"""
    user = user_service.fetch_by_email(db, data.email)
    if not user:
        return success_response(status.HTTP_404_NOT_FOUND, "User not found!")
    data.user_id = user.id
    data.full_name = f"{user.first_name} {user.last_name}"
    new_squeeze = squeeze_service.create(background_tasks, db, data)
    return success_response(status.HTTP_201_CREATED, SUCCESS, new_squeeze.to_dict())


@squeeze.get("", response_model=success_response, status_code=200)
def get_all_squeeze(
    filter: FilterSqueeze = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Get all squeeze pages"""
    squeeze_pages = squeeze_service.fetch_all(db, filter)
    return success_response(status.HTTP_200_OK, SUCCESS, squeeze_pages)


@squeeze.get("/{squeeze_id}", response_model=success_response, status_code=200)
def get_squeeze(
    squeeze_id: str,
    filter: FilterSqueeze = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Get a squeeze page"""
    squeeze_page = squeeze_service.fetch(db, squeeze_id, filter)
    if not squeeze_page:
        return success_response(status.HTTP_404_NOT_FOUND, "Squeeze page not found!")
    return success_response(status.HTTP_200_OK, SUCCESS, squeeze_page)

@squeeze.delete("/{squeeze_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_squeeze(squeeze_id: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    """Delete a squeeze page"""
    squeeze_service.delete(db, squeeze_id)