from sqlalchemy.orm import Session
from fastapi import Depends

from api.v1.models.organization import Organization
from api.v1.models.user import User
from api.db.database import get_db
from api.v1.services.user import user_service

class UserOrganisationsService:
    def get_user_organizations(self, db: Session, user_id: str):
        """Fetches all organizations the user belongs to"""
        return db.query(Organization).filter(Organization.user_id == user_id).all()

    def get_current_user(
        self, access_token: str = Depends(user_service.oauth2_scheme), db: Session = Depends(get_db)
    ) -> User:
        """Function to get current logged-in user"""
        return user_service.get_current_user(access_token, db)

user_organisations_service = UserOrganisationsService()
