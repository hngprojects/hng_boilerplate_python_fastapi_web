from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.profile import Profile
from api.v1.schemas.profile import ProfileCreateUpdate
from api.v1.models.user import User


class ProfileService(Service):
    """Profile service functionality"""

    def create(self, db: Session, schema: ProfileCreateUpdate, user_id: str):
        """Create a new Profile"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if profile:
            raise HTTPException(status_code=400, detail="User profile already exists")

        new_profile = Profile(**schema.model_dump(), user_id=user_id)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)

        return new_profile

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all Profiles with option to search using query parameters"""

        query = db.query(Profile)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Profile, column) and value:
                    query = query.filter(getattr(Profile, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a user by their id"""

        profile = check_model_existence(db, Profile, id)
        return profile

    def fetch_by_user_id(self, db: Session, user_id: str):
        """Fetches a user by their id"""

        profile = db.query(Profile).filter(Profile.user_id == user_id).first()

        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        return profile

    def update(self, db: Session, schema: ProfileCreateUpdate, user_id: str) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Update only the fields that are provided in the schema
        for field, value in schema.model_dump().items():
            if value is not None:
                setattr(profile, field, value)

        for key, value in schema.dict(exclude_unset=True).items():
            setattr(profile, key, value)

        profile.updated_at = datetime.now()
        db.commit()
        db.refresh(profile)
        return profile

    def delete(self, db: Session, id: str):
        """Deletes a profile"""

        profile = self.fetch(id=id)
        db.delete(profile)
        db.commit()

    def fetch_user_by_id(self, db: Session, user_id: str):
        """Fetches a user by their id"""

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User  not found")

        return user
    def update_user_avatar(self, db: Session, user_id: int, avatar_url: str):
        user = self.fetch_user_by_id(db, user_id)
        if user:
            user.avatar_url = avatar_url
            db.commit()
        else:
            raise Exception("User not found")


profile_service = ProfileService()
