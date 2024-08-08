from sqlalchemy.orm import Session
from api.v1.models.permissions.permissions import Permission
from api.v1.models.permissions.role import Role
from api.v1.schemas.permissions.permissions import PermissionCreate
from api.utils.success_response import success_response
from api.v1.models.permissions.role_permissions import role_permissions
from uuid import UUID
from fastapi import HTTPException,status
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from sqlalchemy import delete

class PermissionService:
    @staticmethod
    def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        try:
            db_permission = Permission(title=permission.title)
            db.add(db_permission)
            db.commit()
            db.refresh(db_permission)
            response = success_response(200, "permissions created successfully", db_permission)
            return response
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="A permission with this title already exists.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
        
        
    @staticmethod
    def assign_permission_to_role(db: Session, role_id: str, permission_id: str):
        try:
            # Check if the role exists
            role = db.query(Role).filter_by(id=role_id).first()
            if not role:
                # issue with global http exception handler
                response = {
                    "status": False,
                    "status_code" : status.HTTP_404_NOT_FOUND,
                    "message": "Role not found."
                }
                return JSONResponse(content=response, status_code=status.HTTP_404_NOT_FOUND)       
                 
            # Check if the permission exists
            permission = db.query(Permission).filter_by(id=permission_id).first()
            if not permission:
                raise HTTPException(status_code=404, detail="Permission not found.")
            
            # Assign the permission to the role
            stmt = role_permissions.insert().values(role_id=role_id, permission_id=permission_id)
            db.execute(stmt)
            db.commit()
            
            response = success_response(200, "Permission assigned successfully")
            return response

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="This permission already exists for the role")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
   
    @staticmethod
    def delete_permission(db:Session, permission_id : str):
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission :
            try:
                db.execute(delete(role_permissions).where(role_permissions.c.permission_id == permission_id))
                db.delete(permission)
                db.commit()
                return {}
            except IntegrityError as e :
               db.rollback()
               raise HTTPException(status_code=400, detail="A Permission with this title already exists.")
            except Exception as e:
               db.rollback()
               raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')
    
    @staticmethod
    def update_permission_on_role(db: Session, role_id: str, permission_id: str, new_permission_id: str):
        role = db.query(Role).filter_by(id=role_id).first()
        # Check if the role exists
        if not role:
            raise HTTPException(status_code=404, detail="Role not found.")
        new_permission = db.query(Permission).filter_by(id=new_permission_id).first()
        if not new_permission:
            raise HTTPException(status_code=404, detail="New permission not found.")
        try:
            
            # Check if the new permission exists
            # Remove the old permission from the role
            db.execute(delete(role_permissions).where(role_permissions.c.role_id == role_id).where(role_permissions.c.permission_id == permission_id))

            # Assign the new permission to the role
            db.execute(role_permissions.insert().values(role_id=role_id, permission_id=new_permission_id))
            db.commit()
            return {"success": True, "message": "Permission updated successfully"}

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="An error occurred while updating the permission.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
                
permission_service = PermissionService()
