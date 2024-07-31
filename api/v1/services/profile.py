from typing import Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.profile import Profile
from api.v1.schemas.profile import ProfileCreateUpdate
from api.v1.models.user import User


class ProfileService(Service):
    '''Profile service functionality'''

    def create(self, db: Session,  schema:ProfileCreateUpdate,  user_id: str):
        '''Create a new Profile'''
        profile = db.query(Profile).filter(Profile.user_id==user_id).first()
        
        if profile:
            raise HTTPException(status_code=400, detail="User profile already exist")
        
        new_Profile = Profile(**schema.model_dump(), user_id=user_id)
        db.add(new_Profile)
        db.commit()
        db.refresh(new_Profile)

        return new_Profile
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all Profiles with option tto search using query parameters'''

        query = db.query(Profile)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Profile, column) and value:
                    query = query.filter(getattr(Profile, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, id: str):
        '''Fetches a user by their id'''

        profile = check_model_existence(db, Profile, id)
        return profile
    
    def fetch_by_user_id(self, db: Session, user_id: str):
        '''Fetches a user by their id'''

        profile = db.query(Profile).filter(Profile.user_id==user_id).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return profile
    

    def update(self, db: Session, schema:ProfileCreateUpdate,  user_id: str):
        '''Updates a Profile'''

        profile = self.fetch_by_user_id(db, user_id)
        
        # Update the fields with the provided schema data
        update_data = schema.model_dump()
        for key, value in update_data.items():
            setattr(profile, key, value)
        
        db.commit()
        db.refresh(profile)
        return profile
    

    def delete(self, db: Session, id: str):
        '''Deletes a profile'''
        
        profile = self.fetch(id=id)
        db.delete(profile)
        db.commit()

profile_service = ProfileService()




from api.v1.schemas import UserAndProfileUpdate

def update_user_and_profile(db: Session, user_id: int, user_profile: UserAndProfileUpdate) -> User:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        # Update User fields
        user_data = user_profile.dict(exclude_unset=True, include={"first_name", "last_name", "email", "preferences"})
        for key, value in user_data.items():
            setattr(db_user, key, value)
        
        # Update Profile fields
        profile_data = user_profile.dict(exclude_unset=True, exclude={"first_name", "last_name", "email", "preferences"})
        db_profile = db_user.profile
        if db_profile:
            for key, value in profile_data.items():
                setattr(db_profile, key, value)
        else:
            db_profile = Profile(user_id=user_id, **profile_data)
            db.add(db_profile)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


    