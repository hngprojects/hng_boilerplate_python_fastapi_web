import time
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.schemas.organisation import (
    CreateUpdateOrganisation,
    PaginatedOrgUsers,
    OrganisationBase,
)
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.organisation import organisation_service

from typing import Annotated

organisation = APIRouter(prefix="/organisations", tags=["Organisations"])


@organisation.post(
    "", response_model=success_response, status_code=status.HTTP_201_CREATED
)
def create_organisation(
    schema: CreateUpdateOrganisation,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to create a new organisation"""

    new_org = organisation_service.create(
        db=db,
        schema=schema,
        user=current_user,
    )

    # For some reason this line is needed before data can show in the response
    print("Created Organisation:", new_org)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Organisation created successfully",
        data=jsonable_encoder(new_org),
    )


@organisation.get(
    "/{org_id}/users",
    response_model=success_response,
    status_code=status.HTTP_200_OK,
)
async def get_organisation_users(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
    skip: int = 1,
    limit: int = 10,
):
    """Endpoint to fetch all users in an organisation"""

    return organisation_service.paginate_users_in_organisation(db, org_id, skip, limit)


@organisation.get("/{org_id}/users/export", status_code=200)
async def export_organisation_member_data_to_csv(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to export organisation users data to csv"""

    csv_file = organisation_service.export_organisation_members(db=db, org_id=org_id)

    # Stream the response as a CSV file download
    response = StreamingResponse(csv_file, media_type="text/csv")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=organisation_{org_id}_members.csv"
    )
    response.status_code = 200

    return response


@organisation.patch("/{org_id}", response_model=success_response, status_code=200)
async def update_organisation(
    org_id: str,
    schema: CreateUpdateOrganisation,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to update organisation"""

    updated_organisation = organisation_service.update(db, org_id, schema, current_user)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Organisation updated successfully",
        data=jsonable_encoder(updated_organisation),
    )


@organisation.get("", status_code=status.HTTP_200_OK)
def get_all_organisations(
    super_admin: Annotated[User, Depends(user_service.get_current_super_admin)],
    db: Session = Depends(get_db),
):
    orgs = organisation_service.fetch_all(db)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Retrived all organisations information Successfully",
        data=jsonable_encoder(orgs),
    )


@organisation.delete("/{org_id}")
async def delete_organisation(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    check = organisation_service.check_organisation_exist(db, org_id)
    if check:
        organisation_service.delete(db, id=org_id)
        return success_response(
            status_code=status.HTTP_200_OK,
            message="Organisation with ID {org_id} deleted successfully",
        )