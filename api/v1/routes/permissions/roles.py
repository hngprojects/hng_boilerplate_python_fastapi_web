from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.schemas.permissions.roles import (
    RoleCreate, RoleResponse, RoleAssignRequest, RemoveUserFromRoleResponse
)
from api.v1.services.permissions.role_service import role_service
from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.utils.success_response import success_response
from api.v1.services.organization import organization_service as org_service

role_perm = APIRouter(tags=["permissions management"])

@role_perm.post("/roles", tags=["create role"])
def create_role_endpoint(
    role: RoleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)):
    return  role_service.create_role(db, role)


@role_perm.post("/organizations/{org_id}/users/{user_id}/roles", tags=["assign role to a user"])
def assign_role(
    request: RoleAssignRequest,
    org_id: str = Path(..., description="The ID of the organization"),
    user_id: str = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    return role_service.assign_role_to_user(db, org_id, user_id, request.role_id)


@role_perm.put("/organizations/{org_id}/users/{user_id}/roles/{role_id}", 
               response_model=RemoveUserFromRoleResponse)
def remove_user_from_role(
    org_id: str = Path(..., description="The ID of the organization"),
    user_id: str = Path(..., description="The ID of the user"),
    role_id: str = Path(..., description="The ID of the role"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Endpoint to remove a user from a particular role by `admin`
    """
    admin_role = org_service.get_organization_user_role(current_user.id, org_id, db)
    if (not admin_role) or (admin_role.name != "admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient permission. Admin required."
        )
    
    org = org_service.fetch(db=db, id=org_id)

    user = user_service.fetch(db=db, id=user_id)

    role = role_service.fetch(db=db, role_id=role_id)

    role_service.remove_user_from_role(db, org.id, user.id, role)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="User successfully removed from role"
    )

