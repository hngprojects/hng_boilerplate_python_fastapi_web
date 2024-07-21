from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.schemas.role import RoleCreate
from api.v1.models.user import User
from api.v1.models.role import Role
from api.db.database import get_db
from api.v1.models.permission import Permission
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.utils.auth import get_current_admin

router = APIRouter()

@router.post("/roles", response_model=RoleCreate, status_code=status.HTTP_201_CREATED)
def create_role(role: RoleCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    db_role = db.query(Role).filter(Role.role_name == role.role_name).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    db_organization = db.query(Organization).filter(Organization.id == role.organization_id).first()
    if not db_organization:
        raise HTTPException(status_code=400, detail="Organization does not exist")

    permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
    if len(permissions) != len(role.permission_ids):
        raise HTTPException(status_code=400, detail="Some permissions do not exist")

    new_role = Role(
        role_name=role.role_name,
        organization_id=role.organization_id,
        permissions=permissions
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role
