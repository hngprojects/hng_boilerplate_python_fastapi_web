import time
import logging
from fastapi import Depends, APIRouter, status, HTTPException,Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.models.permissions.user_org_role import user_organisation_roles

from api.v1.models.invitation import Invitation

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

# Ger all organisation invites
@organisation.get("/invites", status_code=status.HTTP_200_OK)
async def get_organisation_invitations(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
    page: int = Query(1, alias="page", description="Page number"),
    page_size: int = Query(10, alias="page_size", description="Number of invites per page"),
):
    """
    Endpoint to fetch all organisation invitations with pagination.
    """
    try:

        invitations, total_count = organisation_service.fetch_all_invitations(db, page, page_size)
        return success_response(
            status_code=status.HTTP_200_OK,
            message="Invites fetched successfully",
            data={
                "invitations": jsonable_encoder(invitations),
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
            }
        )
    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to retrieve organisation invites: {str(e)}"
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

@organisation.delete("/{org_id}/users/{user_id}")
async def remove_user_from_organisation(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """
    Endpoint to remove a user from an organisation
    """

    organisation = organisation_service.get_organisation_by_id(db, org_id)
    if not organisation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation not found",
        )

    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_in_org = db.execute(user_organisation_roles.select().where(
        (user_organisation_roles.c.organisation_id == org_id) &
        (user_organisation_roles.c.user_id == user_id)
    )).fetchone()

    if not user_in_org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of this organisation",
        )

    db.execute(user_organisation_roles.delete().where(
        (user_organisation_roles.c.organisation_id == org_id) &
        (user_organisation_roles.c.user_id == user_id)
    ))
    db.commit()

    return {
        "message": "User successfully removed from organisation",
        "success": True,
        "status_code": 200
    }