from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import CreateUpdateOrganization
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service
from api.v1.schemas.organization import OrganizationBase
from api.v1.services.organization import organization_service
from api.v1.services.user import user_service, oauth2_scheme


organization = APIRouter(prefix="/organizations", tags=["Organizations"])


@organization.post('', response_model=success_response, status_code=status.HTTP_201_CREATED)
async def create_organization(
    schema: CreateUpdateOrganization,
    db: Session= Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user),
):
    '''Endpoint to create a new organization'''

    new_org = organization_service.create(
        db=db,
        schema=schema,
        user=current_user,
    )

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Organization created successfully',
        data=jsonable_encoder(new_org)
    )


"""Endpoint to get an organization"""

@organization.get('/{org_id}', response_model=OrganizationBase, status_code=status.HTTP_200_OK)
def read_organization(org_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = user_service.get_current_user(token, db)
    organization = organization_service.get_organization(db, org_id)
    return {
        "status": "success",
        "status_code": 200,
        "data": organization
    }



@organization.patch('/{org_id}', response_model=success_response)
async def update_organization(org_id: str, schema: CreateUpdateOrganization, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """update organization"""
    updated_organization = organization_service.update(db, org_id, schema, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='Organization updated successfully',
        data=jsonable_encoder(updated_organization)
    )
