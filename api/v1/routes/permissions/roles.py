from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from api.v1.schemas.permissions.roles import (
    RoleCreate,
    RoleResponse,
    RoleAssignRequest,
    RemoveUserFromRoleResponse,
)
from typing import List
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.services.permissions.role_service import role_service
from api.v1.schemas.permissions.roles import RoleDeleteResponse, RoleUpdate
from fastapi.responses import JSONResponse
from api.utils.success_response import success_response

from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.utils.success_response import success_response
from api.v1.services.organisation import organisation_service as org_service

role_perm = APIRouter(tags=["permissions management"])


@role_perm.post("/custom/roles", tags=["Create Custom Role"])
def create_custom_role_endpoint(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    # Ensure it's a custom role
    role.is_builtin = False
    return role_service.create_role(db, role)


@role_perm.post("/built-in/roles", tags=["Create Built-in Role"])
def create_built_in_role_endpoint(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):  # Only super admin can create
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can create built-in roles.",
        )
    # ):

    # Ensure it's a built-in role
    role.is_builtin = True
    return role_service.create_role(db, role)


@role_perm.post(
    "/organisations/{org_id}/users/{user_id}/roles", tags=["assign role to a user"]
)
def assign_role(
    request: RoleAssignRequest,
    org_id: str = Path(..., description="The ID of the organisation"),
    user_id: str = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    return role_service.assign_role_to_user(db, org_id, user_id, request.role_id)


@role_perm.put(
    "/organisations/{org_id}/users/{user_id}/roles/{role_id}",
    response_model=RemoveUserFromRoleResponse,
)
def remove_user_from_role(
    org_id: str = Path(..., description="The ID of the organisation"),
    user_id: str = Path(..., description="The ID of the user"),
    role_id: str = Path(..., description="The ID of the role"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """
    Endpoint to remove a user from a particular role by `admin`
    """
    # GET org
    org = org_service.fetch(db=db, id=org_id)

    # CONFIRM current_user is admin
    org_service.check_user_role_in_org(db, current_user, org, "admin")

    # GET user
    user = user_service.fetch(db=db, id=user_id)

    # GET role
    role = role_service.fetch(db=db, role_id=role_id)

    # REMOVE user from role
    role_service.remove_user_from_role(db, org.id, user.id, role)

    return success_response(
        status_code=status.HTTP_200_OK, message="User successfully removed from role"
    )


@role_perm.delete(
    "/roles/{role_id}", tags=["delete role"], response_model=success_response
)
def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """ An endpoint that fetches all product comment"""
    role_service.delete_role(db, role_id)
    return success_response(
        status_code=200, message="Role successfully deleted.", data={"id": role_id}
    )


@role_perm.get(
    "/organisations/{org_id}/roles",
    response_model=List[RoleResponse],
    tags=["Fetch Roles"],
)
def get_roles_for_organisation(
    org_id: str = Path(..., description="The ID of the organisation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    roles = (role_service.get_roles_by_organisation(db, org_id),)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roles not found for the given organisation",
        )
    return success_response(
        status_code=status.HTTP_200_OK, message="Roles fetched successfully", data=roles
    )


@role_perm.put("/roles/{role_id}/permissions", tags=["update role permissions"])
def update_role_permissions(
    role_id: str,
    permissions: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    updated_role = role_service.update_role_permissions(db, role_id, permissions)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Role permissions updated successfully",
        data=updated_role,
    )


@role_perm.put("/custom/roles/{role_id}", tags=["Update Custom Role"])
def update_custom_role_endpoint(
    role_id: str,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    # Ensure it's a custom role
    role_update.is_builtin = False
    return role_service.update_role(db, role_id, role_update)


@role_perm.put("/built-in/roles/{role_id}", tags=["Update Built-in Role"])
def update_builtin_role_endpoint(
    role_id: str,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can update built-in roles.")
    # Ensure it's a built-in role
    role_update.is_builtin = True
    return role_service.update_builtin_role(db, role_id, role_update)
