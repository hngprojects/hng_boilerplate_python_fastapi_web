from fastapi import HTTPException
from typing import Any, Optional
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.associations import user_organization_association
from api.v1.models.organization import Organization
from api.v1.models.user import User
from api.v1.schemas.organization import (
    CreateUpdateOrganization,
)


class OrganizationService(Service):
    '''Organization service functionality'''

    def create(self, db: Session, schema: CreateUpdateOrganization, user: User):
        '''Create a new organization'''

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
        '''Fetch all organization with option tto search using query parameters'''

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
    

    def update(self, db: Session, id: str, schema):
        '''Updates a organization information'''

        organization = self.fetch(db=db, id=id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(organization, key, value)
        
        db.commit()
        db.refresh(organization)
        return organization

    def delete(self, db: Session, org_id: str, current_user: User):
        """delete an organisation by the owner"""
        organization = db.query(Organization).filter_by(id=org_id).first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        user_org_association = db.query(user_organization_association).filter_by(
            organization_id=org_id,
            user_id=current_user.id
        ).first()

        if not user_org_association:
            raise HTTPException(
                status_code=403,
                detail="User not associated with the organization"
            )

        if user_org_association.role != 'owner':
            raise HTTPException(
                status_code=403,
                detail="You have to be the organization owner to delete an organization"
            )

        db.delete(organization)
        db.commit()

    def add_user(self, db: Session, org_id: str, payload: dict, current_user: User):
        """This service will allow an organization owner to add user to his organization"""

        organization = db.query(Organization).filter_by(id=org_id).first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        organization_owner_id = organization.owner

        if current_user.id != organization_owner_id:
            raise HTTPException(
                status_code=403, detail="Only organization owner can add user"
            )

        user = db.query(User).filter_by(id=payload.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if the user is already a member of the organization
        user_org_association = db.query(user_organization_association).filter_by(
            organization_id=org_id,
            user_id=user.id
        ).first()

        if user_org_association:
            raise HTTPException(status_code=400, detail="User is already a member of the organization")

        # Add user to organization with default role and status
        stmt = user_organization_association.insert().values(
            user_id=user.id,
            organization_id=org_id,
            role='user',  # Default role
            status='member'  # Default status
        )
        db.execute(stmt)
        db.commit()


organization_service = OrganizationService()