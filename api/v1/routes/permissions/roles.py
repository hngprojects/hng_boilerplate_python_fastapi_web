from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.permissions.roles import RoleCreate, RoleResponse, RoleAssignRequest
from api.v1.services.permissions.role_service import role_service
from api.v1.schemas.permissions.roles import RoleDeleteResponse, ResponseModel
from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.models.user import User
from api.v1.services.user import user_service

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


@role_perm.delete("/roles/{role_id}", tags=["delete role"], response_model=ResponseModel)
def delete_role(
    role_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    result = role_service.delete_role(db, role_id)
    
    
    if result:
        return ResponseModel(
            success=True,
            status_code=200,
            message="Role successfully deleted.",
            data={"id": role_id}
        )
    else:
        return ResponseModel(
            success=False,
            status_code=404,
            message="Role not found.",
            data=None
<<<<<<< HEAD
        )
=======
        )
>>>>>>> bf0db3a11038818453904529093396831a74b408
