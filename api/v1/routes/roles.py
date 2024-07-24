from fastapi import APIRouter, Depends, HTTPException, status
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from api.v1.schemas.role import RoleCreate, ResponseModel
from api.db.database import get_db
from api.v1.models import User, Organization, Role, Permission
from api.utils.dependencies import get_current_admin


role = APIRouter(prefix="/roles", tags=["Roles"])


@role.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
def create_role(current_admin: Annotated[User, Depends(get_current_admin)], role: RoleCreate, db: Session = Depends(get_db)):
    db_role = db.query(Role).filter(Role.role_name == role.role_name).first()
    if db_role:
        raise HTTPException(status_code=400, message="Role already exists")

    db_organization = db.query(Organization).filter(Organization.id == role.organization_id).first()
    if not db_organization:
        raise HTTPException(status_code=400, message="Organization does not exist")

    permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
    if len(permissions) != len(role.permission_ids):
        raise HTTPException(status_code=400, message="Some permissions do not exist")

    new_role = Role(
        role_name=role.role_name,
        organization_id=role.organization_id,
        permissions=permissions
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return ResponseModel(message="Role created successfully", status_code=201)
