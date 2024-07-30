from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.services.user_organisations import user_organisations_service
from api.db.database import get_db
from api.v1.models.user import User

user_organisations = APIRouter(prefix="/organizations", tags=["Organizations"])

@user_organisations.get("/", status_code=status.HTTP_200_OK)
def get_user_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_organisations_service.get_current_user),
):
    """Endpoint to get organizations based on user role (superuser or normal user)."""
    organizations = user_organisations_service.get_user_organizations(db=db, user=current_user)
    return success_response(
        status_code=200,
        message="Organizations retrieved successfully",
        data=[org.to_dict() for org in organizations],
    )
