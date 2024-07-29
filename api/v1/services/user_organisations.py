from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.organization import Organization
from api.v1.services.user import user_service
from api.v1.models.user import User

class UserOrganisationsService:
    def get_user_organizations(self, db: Session, user: User):
        """Fetches organizations based on user role (superuser or normal user)."""
        if user.is_super_admin:
            organizations = db.query(Organization).all()
        else:
            organizations = db.query(Organization).join(Organization.users).filter(User.id == user.id).all()
        return organizations

    def get_current_user(
        self, access_token: str = Depends(user_service.oauth2_scheme), db: Session = Depends(get_db)
    ) -> User:
        """Fetches the current user based on the provided access token."""
        return user_service.get_current_user(access_token=access_token, db=db)

user_organisations_service = UserOrganisationsService()
