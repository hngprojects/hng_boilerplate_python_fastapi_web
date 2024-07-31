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

  
@organization.get('/{org_id}', response_model=OrganizationBase, status_code=status.HTTP_200_OK)
def get_organization(org_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = user_service.get_current_user(token, db)
    
    """Endpoint to get an Organization by id"""
    organization = organization_service.fetch(db, org_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return {
        "status": "success",
        "status_code": 200,
        "data": organization
    }
