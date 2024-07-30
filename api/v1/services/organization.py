import logging
from typing import Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import select
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence, check_user_in_org
from api.v1.models.product import Product
from api.v1.models.associations import user_organization_association
from api.v1.models.organization import Organization
from api.v1.models.user import User
from api.v1.schemas.organization import (
    CreateUpdateOrganization, 
    AddUpdateOrganizationRole, 
    RemoveUserFromOrganization
)


class OrganizationService(Service):
    '''Organization service functionality'''

    def create(self, db: Session, schema: CreateUpdateOrganization, user: User):
        '''Create a new product'''

        # Create a new organization
        new_organization = Organization(**schema.model_dump())
        db.add(new_organization)
        db.commit()
        db.refresh(new_organization)

        # Add user as owner to the new organization
        stmt = user_organization_association.insert().values(
            user_id=user.id,
            organization_id=new_organization.id,
            role='owner'
        )
        db.execute(stmt)
        db.commit()

        return new_organization
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all products with option tto search using query parameters'''

        query = db.query(Organization)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Organization, column) and value:
                    query = query.filter(getattr(Organization, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, id: str):
        '''Fetches an organization by id'''

        organization = check_model_existence(db, Organization, id)
        return organization 


    def get_organization_user_role(self, user_id: str, org_id: str, db: Session):
        try:
            stmt = select(user_organization_association.c.role).where(
                user_organization_association.c.user_id == user_id,
                user_organization_association.c.organization_id == org_id
            )
            result = db.execute(stmt).scalar_one_or_none()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    def update(self, db: Session, id: str, schema, current_user: User):
        '''Updates a product'''

        organization = self.fetch(db=db, id=id)

        # check if the current user has the permission to update the organization
        role = self.get_organization_user_role(current_user.id, id, db)
        if role not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(organization, key, value)
        
        db.commit()
        db.refresh(organization)
        return organization
    

    def delete(self, db: Session, id: str):
        '''Deletes a product'''
        
        product = self.fetch(id=id)
        db.delete(product)
        db.commit()

    
    def check_user_role_in_org(self, db: Session, user: User, org: Organization, role: str):
        '''Check user role in organization'''

        if role not in ['user', 'guest', 'admin', 'owner']:
            raise HTTPException(status_code=400, detail="Invalid role")

        stmt = user_organization_association.select().where(
            user_organization_association.c.user_id == user.id,
            user_organization_association.c.organization_id == org.id,
            user_organization_association.c.role == role
        )

        result = db.execute(stmt).fetchone()

        if result is None:
            raise HTTPException(status_code=403, detail=f"Permission denied as user is not of {role} role")

    
    # def update_user_role(self, schema: AddUpdateOrganizationRole, db: Session, org_id: str, user_to_update_id: str):
    # def update_user_role(self, schema: AddUpdateOrganizationRole, db: Session):
    #     '''Updates a user role'''

    #     # Fetch the user and organization
    #     user = check_model_existence(db, User, schema.user_id)
    #     organization = check_model_existence(db, Organization, schema.org_id)

    #     # Check if user is not in organization
    #     check_user_in_org(user, organization)

    #     # Update user role
    #     stmt = user_organization_association.update().where(
    #         user_organization_association.c.user_id == schema.user_id,
    #         user_organization_association.c.organization_id == schema.org_id,
    #     ).values(role=schema.role)

    #     db.execute(stmt)
    #     db.commit()


    # def add_user_to_organization(self, db: Session, org_id: str, user_id: str):
    def add_user_to_organization(self, schema: AddUpdateOrganizationRole, db: Session):
        '''Deletes a user from an organization'''

        # Fetch the user and organization
        user = check_model_existence(db, User, schema.user_id)
        organization = check_model_existence(db, Organization, schema.org_id)

        # Check if user is not in organization
        check_user_in_org(user, organization)
        
        # Check for user role permissions
        self.check_user_role_in_org(db=db, user=user, org=organization, role='admin')\
              or self.check_user_role_in_org(db=db, user=user, org=organization, role='owner')

        # Update user role
        stmt = user_organization_association.insert().values(
            user_id=user.id,
            organization_id=organization.id,
            role=schema.role
        )

        db.execute(stmt)
        db.commit()


    # # def remove_user_from_organization(self, db: Session, org_id: str, user_id: str):
    # def remove_user_from_organization(self, schema: AddRemoveUserFromOrganization, db: Session):
    #     '''Deletes a user from an organization'''

    #     # Fetch the user and organization
    #     user = check_model_existence(db, User, schema.user_id)
    #     organization = check_model_existence(db, Organization, schema.org_id)

    #     # Check if user is not in organization
    #     check_user_in_org(user, organization)

    #     # Check for user role permissions
    #      self.check_user_role_in_org(db=db, user=user, org=organization, role='admin')\
    #       or self.check_user_role_in_org(db=db, user=user, org=organization, role='owner')

    #     # Update user role
    #     stmt = user_organization_association.delete().where(
    #         user_organization_association.c.user_id == schema.user_id,
    #         user_organization_association.c.organization_id == schema.org_id,
    #     )

    #     db.execute(stmt)
    #     db.commit()

    
    # def get_users_in_organization(self, db: Session, org_id: str):
    #     '''Fetches all users in an organization'''

    #     organization = check_model_existence(db, Organization, org_id)
        
    #     # Fetch all users associated with the organization
    #     return organization.users
    

    # def get_user_organizations(self, db: Session, user_id: str):
    #     '''Fetches all organizations that belong to a user'''

    #     user = check_model_existence(db, User, user_id)
        
    #     # Fetch all users associated with the organization
    #     return user.organizations


organization_service = OrganizationService()
