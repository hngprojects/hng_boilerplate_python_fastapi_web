from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import List

from api.db.database import get_db
from api.utils.success_response import success_response
from api.v1.models.organization import Organization
from api.v1.models.user import User
from api.v1.services.user_organisations import user_organisations_service

user_organisations = APIRouter(prefix="/organizations", tags=["Organizations"])

@user_organisations.get("/current-user", status_code=status.HTTP_200_OK)
def get_current_user_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_organisations_service.get_current_user),
):
    """Endpoint to get current user's organizations"""
    organizations = user_organisations_service.get_user_organizations(db, current_user.id)
    return success_response(
        status_code=200,
        message="User organizations retrieved successfully",
        data=organizations,
    )
