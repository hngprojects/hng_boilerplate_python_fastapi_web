from sqlalchemy.orm import Session
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.models.permissions.role_permissions import role_permissions
from api.v1.schemas.permissions.roles import RoleDeleteResponse
from api.v1.models.permissions.permissions import Permission
from api.v1.schemas.permissions.roles import RoleCreate, RoleUpdate
from uuid_extensions import uuid7
from api.utils.success_response import success_response
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, insert
from api.utils.db_validators import check_model_existence
from api.v1.services.organisation import organisation_service as org_service


class RoleService:

    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        try:
            db_role = Role(
                name=role.name, 
                is_builtin=role.is_builtin, 
                description=role.description or ""
                )
            db.add(db_role)
            db.commit()
            db.refresh(db_role)
            response = success_response(201, f'Role {role.name} created successfully', db_role)
            return response
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="A role with this name already exists."
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred: " + str(e)
            )

    @staticmethod
    def assign_role_to_user(db: Session, org_id: uuid7, user_id: uuid7, role_id: uuid7):
        user_org = db.execute(
            user_organisation_roles.select().where(
                user_organisation_roles.c.user_id == user_id,
                user_organisation_roles.c.organisation_id == org_id,
            )
        ).fetchone()
        if not user_org:
            raise HTTPException(status_code=404, detail="User is not part of the organisation")
        

        if user_org.role_id is not None:
            raise HTTPException(status_code=400, detail="User already has a role in the organisation")
        
        try:
        # Update the role_id for the user-organisation pair
            stmt = update(user_organisation_roles).where(
                user_organisation_roles.c.user_id == user_id,
                user_organisation_roles.c.organisation_id == org_id,
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
    def get_roles_by_organisation(db: Session, organisation_id: str):
        roles = (
            db.query(Role)
            .join(user_organisation_roles, Role.id == user_organisation_roles.c.role_id)
            .filter(user_organisation_roles.c.organisation_id == organisation_id)
            .all()
        )
        if not roles:
            raise HTTPException(
                status_code=404, detail="Roles not found for the given organisation"
            )
        return roles

    def fetch(self, db: Session, role_id: str):
        """Fetches an role by id"""

        role = check_model_existence(db, Role, role_id)

        return role

    def get_user_role_relation(self, db: Session, user_id: str, org_id: str, role: Role):
        '''Get the relation with user_id, role.id, and org_id exist'''

        if role.name not in ['user', 'guest', 'admin', 'owner']:
            raise HTTPException(status_code=400, detail="Invalid role")

        stmt = user_organisation_roles.select().where(
            user_organisation_roles.c.user_id == user_id,
            user_organisation_roles.c.organisation_id == org_id,
            user_organisation_roles.c.role_id == role.id,
        )

        relation = db.execute(stmt).fetchone()

        if relation is None:
            raise HTTPException(status_code=403, detail="User not found in role")
        
        return relation

    def remove_user_from_role(self, db: Session, org_id: str, user_id: str, role: Role):
        """Delete user role relationship"""
        if self.get_user_role_relation(db, user_id, org_id, role):
            db.execute(user_organisation_roles.delete().where(
                user_organisation_roles.c.user_id == user_id,
                user_organisation_roles.c.organisation_id == org_id,
                user_organisation_roles.c.role_id == role.id,
            ))
            db.commit()
            
    
    @staticmethod
    def update_role(db: Session, role_id: str, role_update: RoleUpdate) -> Role:
        role = db.query(Role).filter_by(id=role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if role.is_builtin != role_update.is_builtin:
            raise HTTPException(status_code=400, detail="Cannot change role type (builtin/custom)")

        role.name = role_update.name
        db.commit()
        db.refresh(role)
        
        response = success_response(200, f'Role {role.name} updated successfully', role)
        return response
    
    
    @staticmethod
    def update_builtin_role(db: Session, role_id: str, role_update: RoleUpdate) -> Role:
        role = db.query(Role).filter_by(id=role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if not role.is_builtin:
            raise HTTPException(status_code=400, detail="Role is not a built-in role")

        role.name = role_update.name
        db.commit()
        db.refresh(role)
        
        response = success_response(200, f'Built-in role {role.name} updated successfully', role)
        return response


role_service = RoleService()
