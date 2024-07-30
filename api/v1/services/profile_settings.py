from sqlalchemy.orm import Session
from api.v1.models import User, Profile
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
