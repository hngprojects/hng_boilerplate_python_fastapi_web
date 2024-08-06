from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi import status
from api.v1.schemas.permissions.permissions import PermissionCreate, PermissionResponse, PermissionAssignRequest
from api.v1.services.permissions.permison_service import permission_service
from api.db.database import get_db
from uuid_extensions import uuid7
from api.v1.models.user import User
from api.v1.services.user import user_service

perm_role = APIRouter(tags=["permissions management"])

@perm_role.post("/permissions", tags=["create permissions"])
def create_permission_endpoint(permission: PermissionCreate, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    return permission_service.create_permission(db, permission)


@perm_role.post("/roles/{role_id}/permissions", tags=["assign role to a user"])
def assign_permission_endpoint(
    request: PermissionAssignRequest,  # Updated to receive request body
    role_id: str = Path(..., description="The ID of the role"),  # Role ID from path
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)):
    return permission_service.assign_permission_to_role(db, role_id,request.permission_id)
    
@perm_role.delete("/permissions/{permission_id}", tags=["Delete permissions"] , status_code=status.HTTP_204_NO_CONTENT)
def delete_permissions(
    permission_id : str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
    ):
    return permission_service.delete_permission(db , permission_id)
