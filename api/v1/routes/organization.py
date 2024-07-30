from fastapi import Depends, APIRouter, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import CreateUpdateOrganization, PaginatedOrgUsers
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service


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


@organization.get(
    '/{org_id}/users',
    response_model=PaginatedOrgUsers,
    status_code=status.HTTP_200_OK,
)
async def get_organization_users(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
    page: int = 1,
    per_page: int = 10
):
    '''Endpoint to fetch all users in an organization'''

    org_users = organization_service.paginate_users_in_organization(
        db, org_id, page, per_page)
    total = organization_service.count_organization_users(db, org_id)

    return PaginatedOrgUsers(
        total=total,
        page=page,
        per_page=per_page,
        success=True,
        status_code=status.HTTP_200_OK,
        message='Organization users fetched successfully',
        data=jsonable_encoder(org_users)
    )
