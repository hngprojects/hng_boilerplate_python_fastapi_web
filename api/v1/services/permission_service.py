from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.v1.models.permission import Permission
from api.v1.schemas.permission import PermissionCreate, PermissionUpdate

def create_permission(db: Session, permission: PermissionCreate):
    db_permission = db.query(Permission).filter(Permission.name == permission.name).first()
    if db_permission:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Permission already exists")
    new_permission = Permission(name=permission.name, description=permission.description)
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission

def get_permissions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Permission).offset(skip).limit(limit).all()

def get_permission(db: Session, permission_id: str):
    return db.query(Permission).filter(Permission.id == permission_id).first()

def update_permission(db: Session, permission_id: str, permission: PermissionUpdate):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    db_permission.name = permission.name
    if permission.description:
        db_permission.description = permission.description
    db.commit()
    db.refresh(db_permission)
    return db_permission

def delete_permission(db: Session, permission_id: str):
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    db.delete(db_permission)
    db.commit()
    return db_permission
