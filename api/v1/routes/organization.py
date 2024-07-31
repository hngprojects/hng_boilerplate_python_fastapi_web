import time
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi import Depends, APIRouter, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import CreateUpdateOrganization, OrganizationBase
from api.v1.schemas.organization import CreateUpdateOrganization, AddUserToOrganization
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service

organization = APIRouter(prefix="/organizations", tags=["Organizations"])

@organization.post('', response_model=success_response, status_code=status.HTTP_201_CREATED)
def create_organization(
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

    # For some reason this line is needed before data can show in the response
    print("Created Organization:", new_org) 

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message='Organization created successfully',
        data=jsonable_encoder(new_org),
    )


@organization.patch('/{org_id}', response_model=success_response, status_code=200)
async def update_organization(
    org_id: str, 
    schema: CreateUpdateOrganization, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)
):
    """Endpoint to update organization"""

    updated_organization = organization_service.update(db, org_id, schema, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message='Organization updated successfully',
        data=jsonable_encoder(updated_organization)
    )

@organization.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """delete organization"""
    organization_service.delete(db, org_id, current_user)
    return success_response(status_code=status.HTTP_204_NO_CONTENT, message='Organization deleted successfully')

@organization.post("/{org_id}", status_code=status.HTTP_201_CREATED)
def add_user_organization(payload: AddUserToOrganization, org_id: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """add user to organization"""
    organization_service.add_user_org(db, current_user, org_id, payload)
    return success_response(status_code=status.HTTP_201_CREATED, message='User added to organization successfully')