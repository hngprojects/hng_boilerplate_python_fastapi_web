from sqlalchemy.orm import Session
from api.v1.models.permissions import Permission
from api.v1.models.role import Role
from api.v1.schemas.permissions import PermissionCreate
from api.v1.models.role_permissions import role_permissions
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class PermissionService:
    @staticmethod
    def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        try:
            db_permission = Permission(name=permission.name)
            db.add(db_permission)
            db.commit()
            db.refresh(db_permission)
            return db_permission
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="A permission with this name already exists.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
        
    @staticmethod
    def assign_permission_to_role(db: Session, role_id: str, permission_id: str):
        try:
            # Check if the role exists
            role = db.query(Role).filter_by(id=role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Role not found.")
            
            # Check if the permission exists
            permission = db.query(Permission).filter_by(id=permission_id).first()
            if not permission:
                raise HTTPException(status_code=404, detail="Permission not found.")
            
            # Assign the permission to the role
            # Ensure role_permissions table exists and create the association
            db.add(role_permissions.insert().values(role_id=role_id, permission_id=permission_id))
            db.commit()
            return {"success": True, "message": "Permission assigned successfully"}

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="An error occurred while assigning the permission.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


permission_service = PermissionService()