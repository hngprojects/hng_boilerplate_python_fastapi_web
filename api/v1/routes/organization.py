from fastapi import Depends, APIRouter, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import CreateUpdateOrganization
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service

from api.v1.schemas.organization import OrganizationAddUser, OrganizationResponse
from api.v1.services.organization import organization_service
from api.v1.services.user import user_service


organization = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)

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

@organization.delete(
    "/{org_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    organization_service.delete(
        db=db,
        org_id=org_id,
        current_user=current_user,
    )

@organization.post(
    "/{org_id}/add-user",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationResponse,
)
def add_user_organization(
    org_id: str, 
    payload: OrganizationAddUser,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    organization_service.add_user(db=db, org_id=org_id, current_user=current_user, payload=payload)
