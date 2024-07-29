from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.user import User
from api.v1.models.organization import Organization


class OrganizationService(Service):

    def delete(
        self, db: Session, org_id: str, current_user: User  # Organization ID to delete
    ):
        organization = db.query(Organization).filter_by(id=org_id).first()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        organization_owner_id = organization.owner.id

        if current_user.id != organization_owner_id:
            raise HTTPException(
                status_code=403,
                detail="you have to be organization owner or admin to delete an organization",
            )

        db.delete(organization)
        db.commit()
        db.refresh(organization)

    def create(self):
        return super().create()

    def fetch_all(self):
        return super().fetch_all()

    def update(self):
        return super().update()

    def fetch(self, db: Session):
        return super().fetch()

    def add_user(
        self,
        db: Session,
        org_id: str,
        payload: dict,
        current_user: User,
    ):
        """This service will allow an organization owner to add user to his organization"""
        organization = db.query(Organization).filter_by(id=org_id).first()
        print(f"Organization is {organization}")

        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        organization_owner_id = organization.owner

        if current_user.id != organization_owner_id:
            raise HTTPException(
                status_code=403, detail="Only organization owner can add user"
            )

        user = db.query(User).filter_by(id=payload.user_id).first()

        # Check if the user is already a member of the organization
        if user in organization.users:
            raise HTTPException(status_code=400, detail="User is already a member of the organization")

        
        organization.users.append(user)
        db.commit()
        db.refresh(organization)


organization_service = OrganizationService()
