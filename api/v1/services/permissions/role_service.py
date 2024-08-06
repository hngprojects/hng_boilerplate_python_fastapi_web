from sqlalchemy.orm import Session
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.user_org_role import user_organization_roles
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from api.v1.schemas.role import RoleCreate
from uuid_extensions import uuid7
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from api.utils.db_validators import check_model_existence
from api.v1.services.organization import organization_service as org_service


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
    def delete_role(db: Session, role_id: str) -> RoleDeleteResponse:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        db.delete(role)
        db.commit()
        return RoleDeleteResponse(id=role_id, message="Role successfully deleted")

    def fetch(self, db: Session, role_id: str):
        """Fetches an role by id"""

        role = check_model_existence(db, Role, role_id)

        return role

    def get_user_role_relation(self, db: Session, user_id: str, org_id: str, role: Role):
        '''Get the relation with user_id, role.id, and org_id exist'''

        if role.name not in ['user', 'guest', 'admin', 'owner']:
            raise HTTPException(status_code=400, detail="Invalid role")

        stmt = user_organization_roles.select().where(
            user_organization_roles.c.user_id == user_id,
            user_organization_roles.c.organization_id == org_id,
            user_organization_roles.c.role_id == role.id,
        )

        relation = db.execute(stmt).fetchone()

        if relation is None:
            raise HTTPException(status_code=403, detail="User not found in role")
        
        return relation

    def remove_user_from_role(self, db: Session, org_id: str, user_id: str, role: Role):
        """Delete user role relationship"""
        if self.get_user_role_relation(db, user_id, org_id, role):
            db.execute(user_organization_roles.delete().where(
                user_organization_roles.c.user_id == user_id,
                user_organization_roles.c.organization_id == org_id,
                user_organization_roles.c.role_id == role.id,
            ))
            db.commit()


role_service = RoleService()