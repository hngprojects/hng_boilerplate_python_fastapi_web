from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from api.v1.schemas.role import RoleCreate, ResponseModel
from api.db.database import get_db
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from api.utils.dependencies import get_current_admin, get_current_user
from api.v1.schemas.permission import PermissionCreate, PermissionResponse, PermissionList, PermissionModel


permission = APIRouter(prefix="/permissions", tags=["Permission"])

@permission.post("/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(current_admin: Annotated[User, Depends(get_current_admin)], permission: PermissionCreate, db: Session = Depends(get_db)):
    db_permission = Permission(name=permission.name)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    response = PermissionResponse(
        id=db_permission.id,
        name=db_permission.name,
        status_code=201,
        message="Permission created successfully"
    )
    return response

# Endpoint to get all permissions
@permission.get("/", response_model=PermissionList, status_code=status.HTTP_200_OK)
def get_permissions(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    permissions = db.query(Permission).all()
    permissions_list = [PermissionModel(id=perm.id, name=perm.name) for perm in permissions]
    perms = {
        "permissions": permissions_list,
        "status_code": 200,
        "message": "Successfully retrieved Permissions"
    }
    perm = PermissionList(**perms)
    return perm