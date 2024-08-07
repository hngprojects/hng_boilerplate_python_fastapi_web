from sqlalchemy.orm import Session
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.user_org_role import user_organization_roles
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from api.v1.models.permissions.permissions import Permission
from api.v1.schemas.permissions.roles import RoleCreate
from uuid_extensions import uuid7
from api.utils.success_response import success_response
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert


class RoleService:

    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        try:
            db_role = Role(name=role.name, is_builtin=role.is_builtin)
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            response = success_response(201, f'Role {role.name} created successfully', db_role)
            return response
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="A role with this name already exists.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

    @staticmethod
    def assign_role_to_user(db: Session, org_id: uuid7, user_id: uuid7, role_id: uuid7):
        user_org = db.execute(
            user_organization_roles.select().where(
                user_organization_roles.c.user_id == user_id,
                user_organization_roles.c.organization_id == org_id,
            )
        ).fetchone()
        if not user_org:
            raise HTTPException(status_code=404, detail="User is not part of the organization")
        

        if user_org.role_id is not None:
            raise HTTPException(status_code=400, detail="User already has a role in the organization")
        
        try:
        # Update the role_id for the user-organization pair
            stmt = update(user_organization_roles).where(
                user_organization_roles.c.user_id == user_id,
                user_organization_roles.c.organization_id == org_id,
            ).values(role_id=role_id)
            
            db.execute(stmt)
            db.commit()

            return success_response(200, "Role assigned to user successfully")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An error occurred while assigning the role: " + str(e))


    @staticmethod
    def delete_role(db: Session, role_id: str) -> RoleDeleteResponse:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        db.delete(role)
        db.commit()
        return RoleDeleteResponse(id=role_id, message="Role successfully deleted")
    
    
    @staticmethod
    def get_roles_by_organization(db: Session, organization_id: str):
        roles = db.query(Role).join(
            user_organization_roles, Role.id == user_organization_roles.c.role_id
        ).filter(user_organization_roles.c.organization_id == organization_id).all()
        if not roles:
            raise HTTPException(status_code=404, detail="Roles not found for the given organization")
        return roles


role_service = RoleService()