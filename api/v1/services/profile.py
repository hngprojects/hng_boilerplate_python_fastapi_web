from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.profile import Profile
from api.v1.schemas.profile import ProfileCreateUpdate, ProfileBase

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

    def fetch_all(self, db: Session, **query_params):
        """Fetch all Profiles with option to search using query parameters"""
        query = db.query(Profile)
        if query_params:
            for column, value in query_params.items():
                if hasattr(Profile, column) and value:
                    query = query.filter(getattr(Profile, column).ilike(f"%{value}%"))
        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a user by their id"""
        return check_model_existence(db, Profile, id)

    def fetch_by_user_id(self, db: Session, user_id: str):
        """Fetches a user by their id"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile

    def update(self, db: Session, schema: ProfileCreateUpdate, user_id: str) -> ProfileBase:
        profile = db.query(Profile).filter_by(user_id=user_id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        for key, value in schema.model_dump().items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return ProfileBase.model_validate(profile)

    def delete(self, db: Session, id: str):
        """Deletes a profile"""
        profile = self.fetch(db, id)
        db.delete(profile)
        db.commit()
        

profile_service = ProfileService()
