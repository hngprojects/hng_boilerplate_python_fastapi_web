from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.schemas.permissions.roles import RoleCreate, RoleResponse, RoleAssignRequest
from api.v1.services.permissions.role_service import role_service
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from fastapi.responses import JSONResponse
from api.utils.success_response import success_response

from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.models.user import User
from api.v1.services.user import user_service

role_perm = APIRouter(tags=["permissions management"])

@role_perm.post("/custom/roles", tags=["Create Custom Role"])
def create_custom_role_endpoint(
    role: RoleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)):
    # Ensure it's a custom role
    role.is_builtin = False
    return role_service.create_role(db, role)

@role_perm.post("/built-in/roles", tags=["Create Built-in Role"])
def create_built_in_role_endpoint(
    role: RoleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_super_admin)):  # Only super admin can create
    if not current_user.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only super admins can create built-in roles.")
    # ):
    
    # Ensure it's a built-in role
    role.is_builtin = True
    return role_service.create_role(db, role)


@role_perm.post("/organizations/{org_id}/users/{user_id}/roles", tags=["assign role to a user"])
def assign_role(
    request: RoleAssignRequest,
    org_id: str = Path(..., description="The ID of the organization"),
    user_id: str = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    return role_service.assign_role_to_user(db, org_id, user_id, request.role_id)


@role_perm.delete("/roles/{role_id}", tags=["delete role"], response_model=success_response)
def delete_role(
    role_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    role_service.delete_role(db, role_id)
    return success_response(status_code=200, message="Role successfully deleted.", data={"id": role_id})
       
    
    
    

@role_perm.get(
    "/organizations/{org_id}/roles",
    response_model=List[RoleResponse],
    tags=["Fetch Roles"],
)
def get_roles_for_organization(
    org_id: str = Path(..., description="The ID of the organization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    roles = (role_service.get_roles_by_organization(db, org_id),)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roles not found for the given organization",
        )
    return success_response(
        status_code=status.HTTP_200_OK, message="Roles fetched successfully", data=roles
    )
