from typing import Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.v1.models.org_role import OrgRole
from api.v1.schemas.org import OrganizationSchema

class OrganizationService():
    """Organization service functionality"""

    def create (self, db: Session, schema:OrganizationSchema):
       """Create Organization"""

       new_organization = Organization(**schema)
       db.add(new_organization)
       db.commit()
       db.refresh(new_organization)

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

    def fetch(self, db: Session, id):
        '''Fetches an Organisation by their id'''

        organization = check_model_existence(db, Organization, id)
        return organization


    def add_user(self, db: Session, org_id: int, user: User):
        '''Adds a current user to an Organisation'''

        # Fetch the organization by ID
        organization = db.query(Organization).filter(Organization.id == org_id).first()
        if organization is None:
            raise HTTPException(status_code=404, detail="Organization not found")


        # Check if the current user is an admin of the organization
        if not self.is_admin_of_org(db, user, organization):
            raise HTTPException(status_code=403, detail="Insufficient permissions to add users to this organization")

        # Fetch the user to be added
        user_to_add = db.query(User).filter(User.id == user.id).first()
        if user_to_add is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the user is already a member of the organization
        if user_to_add in organization.users:
            raise HTTPException(status_code=400, detail="User is already a member of the organization")
        # Add the user to the organization
        organization.users.append(user_to_add)

        # Commit the changes to the database
        db.commit()
        db.refresh(organization)


    def is_admin_of_org(self, db: Session, user: User, organization: Organization) -> bool:
        '''Checks if the user is an admin of the given organization.'''
        return db.query(OrgRole).filter(
            OrgRole.user_id == user.id,
            OrgRole.org_id == organization.id,
            OrgRole.is_admin == True
        ).first() is not None

    def delete(self, db: Session, id: str):
        '''Deletes an Organization'''

        organization = self.fetch(id=id, db=db)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found! ")
        db.delete(organization)
        db.commit()

organization_service = OrganizationService()
