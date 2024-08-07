from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.orm import Session
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


@role_perm.delete("/roles/{role_id}", tags=["delete role"], response_model=success_response)
def delete_role(
    role_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    try:
        result = role_service.delete_role(db, role_id)
        return success_response(status_code=200, message="Role successfully deleted.", data={"id": role_id})
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"status": False, "status_code": e.status_code, "message": e.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": False, "status_code": 500, "message": f"An unexpected error occurred: {str(e)}"})
    
    
    
