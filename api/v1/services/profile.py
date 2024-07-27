import logging
from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.profile import Profile
from api.v1.schemas.profile import ProfileCreateUpdate

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProfileService(Service):
    """Profile service functionality"""

    def create(self, db: Session, schema: ProfileCreateUpdate, user_id: str):
        """Create a new Profile"""
        logger.debug(f"Attempting to create profile for user_id: {user_id}")
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if profile:
            logger.error("User profile already exists")
            raise HTTPException(status_code=400, detail="User profile already exists")

        new_profile = Profile(**schema.model_dump(), user_id=user_id)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        logger.debug(f"Profile created: {new_profile}")
        return new_profile

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all Profiles with option to search using query parameters"""
        logger.debug(f"Fetching all profiles with query params: {query_params}")
        query = db.query(Profile)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Profile, column) and value:
                    query = query.filter(getattr(Profile, column).ilike(f"%{value}%"))

        profiles = query.all()
        logger.debug(f"Found profiles: {profiles}")
        return profiles

    def fetch(self, db: Session, id: str):
        """Fetches a profile by its id"""
        logger.debug(f"Fetching profile with id: {id}")
        profile = check_model_existence(db, Profile, id)
        return profile

    def fetch_by_user_id(self, db: Session, user_id: str):
        """Fetches a profile by user id"""
        logger.debug(f"Fetching profile for user_id: {user_id}")
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if not profile:
            logger.error("User profile not found")
            raise HTTPException(status_code=404, detail="User profile not found")

        return profile

    def update(self, db: Session, schema: ProfileCreateUpdate, user_id: str):
        """Updates a Profile"""
        logger.debug(f"Updating profile for user_id: {user_id}")
        profile = self.fetch_by_user_id(db, user_id)

        # Update the fields with the provided schema data
        update_data = schema.model_dump()
        for key, value in update_data.items():
            setattr(profile, key, value)

        db.commit()
        db.refresh(profile)
        logger.debug(f"Profile updated: {profile}")
        return profile

    def delete(self, db: Session, id: str):
        """Deletes a profile"""
        logger.debug(f"Deleting profile with id: {id}")
        profile = self.fetch(db, id)
        db.delete(profile)
        db.commit()
        logger.debug(f"Profile deleted")


profile_service = ProfileService()
