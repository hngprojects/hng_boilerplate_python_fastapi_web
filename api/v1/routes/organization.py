import time
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import CreateUpdateOrganization, OrganizationBase
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service
from api.v1.schemas.organization import OrganizationBase
from api.v1.services.organization import organization_service
from api.v1.services.user import user_service, oauth2_scheme


organization = APIRouter(prefix="/organizations", tags=["Organizations"])


@organization.get('/{org_id}', response_model=success_response, status_code=status.HTTP_200_OK)
def get_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get an organization by ID"""
    get_organization = organization_service.fetch(db=db, user=current_user)
    return success_response(
        status_code=200,
        message="Organization retrieved successfully",
        data=jsonable_encoder(get_organization)
)
  