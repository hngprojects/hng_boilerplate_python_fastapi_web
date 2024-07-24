from sqlalchemy.orm import Session
from api.v1.models.profile import Profile
from api.v1.schemas.user import UserUpdate


class ProfileService:
    def create_profile(self, db: Session, user_id: str, initial_data: dict):
        """Create a new profile for a user with initial data"""
        profile = Profile(user_id=user_id, **initial_data)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def update_profile(self, db: Session, profile: Profile, schema: UserUpdate):
        """Update the profile based on the schema"""
        for field, value in schema:
            if hasattr(profile, field):
                setattr(profile, field, value)
        db.commit()
        db.refresh(profile)
        return profile
    

profile_service = ProfileService()
