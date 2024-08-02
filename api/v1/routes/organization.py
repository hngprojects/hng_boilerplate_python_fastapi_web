import time
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organization import (
    CreateUpdateOrganization,
    PaginatedOrgUsers,
    OrganizationBase,
)
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.organization import organization_service
from api.v1.services.product import product_service
from api.v1.schemas.product import ProductDetail

from typing import Annotated

organization = APIRouter(prefix="/organizations", tags=["Organizations"])


@organization.post(
    "", response_model=success_response, status_code=status.HTTP_201_CREATED
)
def create_organization(
    schema: CreateUpdateOrganization,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to create a new organization"""

    new_org = organization_service.create(
        db=db,
        schema=schema,
        user=current_user,
    )

    # For some reason this line is needed before data can show in the response
    print("Created Organization:", new_org)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Organization created successfully",
        data=jsonable_encoder(new_org),
    )


@organization.get(
    "/{org_id}/users",
    response_model=success_response,
    status_code=status.HTTP_200_OK,
)
async def get_organization_users(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
    skip: int = 1,
    limit: int = 10,
):
    """Endpoint to fetch all users in an organization"""

    return organization_service.paginate_users_in_organization(db, org_id, skip, limit)


@organization.patch("/{org_id}", response_model=success_response, status_code=200)
async def update_organization(
    org_id: str,
    schema: CreateUpdateOrganization,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to update organization"""

    updated_organization = organization_service.update(db, org_id, schema, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Organization updated successfully",
        data=jsonable_encoder(updated_organization),
    )


@organization.get("", status_code=status.HTTP_200_OK)
def get_all_organizations(
    super_admin: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Session = Depends(get_db),
):
    orgs = organization_service.fetch_all(db)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Retrived all organizations information Successfully",
        data=jsonable_encoder(orgs),
    )


@organization.delete("/{org_id}")
async def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    check = organization_service.check_organization_exist(db, org_id)
    if check:
        organization_service.delete(db, id=org_id)
        return success_response(
            status_code=status.HTTP_200_OK,
            message="Organization with ID {org_id} deleted successfully"
        )


@organization.get(
    "/{org_id}/products/{product_id}",
    response_model=dict[str, int | str | bool | ProductDetail],
    summary="Get product detail",
    description="Endpoint to get detail about the product with the given `id`",
)
async def get_product_detail(
    org_id: str,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """
    Retrieve product detail

    This endpoint retrieve details about a product

    Args:
        org_id (UUID): The unique identifier of the organization
        product_id (UUID): The unique identifier of the product to be retrieved.
        db (Session): The database session, provided by the `get_db` dependency.
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.

    Returns:
        ProductDetail: The detail of the product matching the given id

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.
    """

    product = product_service.fetch_single_by_organization(db, org_id, product_id, current_user)

    return {
        "status_code": status.HTTP_200_OK,
        "success": True,
        "message": "Product fetched successfully",
        "data": product,
    }