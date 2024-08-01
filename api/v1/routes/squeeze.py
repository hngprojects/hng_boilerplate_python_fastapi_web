from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.core.responses import SUCCESS
from api.utils.success_response import success_response
from api.v1.services.squeeze import squeeze_service
from api.v1.schemas.squeeze import CreateSqueeze, UpdateSqueeze
from api.v1.services.user import user_service
from api.v1.models import *

squeeze = APIRouter(prefix="/squeeze", tags=["Squeeze Page"])


@squeeze.post("", response_model=success_response, status_code=201)
def create_squeeze(
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
    new_squeeze = squeeze_service.create(db, data)
    return success_response(status.HTTP_201_CREATED, SUCCESS, new_squeeze.to_dict())


@squeeze.delete("/{squeeze_id}", response_model=success_response)
def delete_squeeze(
    squeeze_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Delete a squeeze page"""
    squeeze_page = squeeze_service.fetch(db, squeeze_id)  # Use fetch instead of get_by_id
    if not squeeze_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Squeeze page not found!")
    squeeze_service.delete(db, squeeze_id)
    return success_response(status.HTTP_200_OK, "Squeeze page deleted successfully!")


@squeeze.put("/{squeeze_id}", response_model=success_response)
def edit_squeeze(
    squeeze_id: int,
    data: UpdateSqueeze,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Edit a squeeze page"""
    squeeze_page = squeeze_service.fetch(db, squeeze_id)  # Use fetch instead of get_by_id
    if not squeeze_page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Squeeze page not found!")
    updated_squeeze = squeeze_service.update(db, squeeze_id, data)
    return success_response(status.HTTP_200_OK, SUCCESS, updated_squeeze.to_dict())
