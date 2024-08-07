from sqlalchemy.orm import Session
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.user_org_role import user_organization_roles
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from api.v1.schemas.role import RoleCreate
from uuid_extensions import uuid7
from api.utils.success_response import success_response
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class RoleService:

    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        try:
            db_role = Role(name=role.name)
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            response = success_response(201, f'role {role.name} created successfully', db_role)
            return response
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="A role with this name already exists.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

    @staticmethod
    def assign_role_to_user(db: Session, org_id: uuid7, user_id: uuid7, role_id: uuid7):
        try:
            db.execute(user_organization_roles.insert().values(
                organization_id=org_id,
                user_id=user_id,
                role_id=role_id
            ))
            db.commit()
            return success_response(200, "role successfully added to user")
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="The role or user might not exist, or there might be a duplication issue.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
        
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