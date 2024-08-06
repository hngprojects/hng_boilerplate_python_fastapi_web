from fastapi import APIRouter, Depends, Path, Query, HTTPException,status
from sqlalchemy.orm import Session
from api.v1.schemas.permissions.roles import RoleCreate, RoleResponse, RoleAssignRequest
from api.v1.services.permissions.role_service import role_service
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

@role_perm.delete("/roles/{role_id}", tags=["delete roles"], status_code=status.HTTP_204_NO_CONTENT)
def delete_role_endpoint(
    role_id : str,
    db : Session=Depends(get_db),
    admin_user : User = Depends(user_service.get_current_super_admin),
   
):
    return role_service.delete_role(db=db,role_id=role_id)
    

@role_perm.post("/organizations/{org_id}/users/{user_id}/roles", tags=["assign role to a user"])
def assign_role(
    request: RoleAssignRequest,
    org_id: str = Path(..., description="The ID of the organization"),
    user_id: str = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    return role_service.assign_role_to_user(db, org_id, user_id, request.role_id)
