from sqlalchemy.orm import Session
from api.v1.models.role import Role
from api.v1.models.user_org_role import user_organization_roles
from api.v1.schemas.roles import RoleCreate
from uuid_extensions import uuid7
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
            return db_role
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
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="The role or user might not exist, or there might be a duplication issue.")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
        
    
    @staticmethod
    def get_roles_by_organization(db: Session, organization_id: str):
        roles = db.query(Role).join(
            user_organization_roles, Role.id == user_organization_roles.c.role_id
        ).filter(user_organization_roles.c.organization_id == organization_id).all()
        return roles


role_service = RoleService()