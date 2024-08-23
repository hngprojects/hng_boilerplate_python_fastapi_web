from fastapi import status
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks, Depends, status
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models import Profile, User
from api.v1.schemas.profile import (ProfileCreateUpdate,
                                    ProfileUpdateResponse,
                                    ProfileData,
                                    ProfileRecoveryEmailResponse,
                                    Token)
from api.core.dependencies.email_sender import send_email
from api.utils.settings import settings
from api.db.database import get_db


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

    def update(self, db: Annotated[Session, Depends(get_db)], schema: ProfileCreateUpdate,
               user: User, background_tasks: BackgroundTasks) -> Profile:
        """
        Updates a user's profile data.
        """
        message = 'Profile updated successfully.'
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Update only the fields that are provided in the schema
        for field, value in schema.model_dump().items():
            if value is not None:
                if field == 'recovery_email':
                    self.send_token_to_user_email(value, user, background_tasks)
                    message = 'Profile updated successfully. Access your email to verify recovery_email'
                    continue
                setattr(profile, field, value)

        db.commit()
        db.refresh(profile)
        return ProfileUpdateResponse(
            message=message,
            status_code=status.HTTP_200_OK,
            data=ProfileData.model_validate(profile, from_attributes=True)
        )
    
    def send_token_to_user_email(self, recovery_email: str, user: User,
                                 background_tasks: BackgroundTasks):
        """
        Mails the token for recovery email to the user.

        Args:
            user: the user object.
            recovery_email: the new recovery_email from the user.
            background_tasks: the background_task object.
        Return:
            response: feedback to the user.
        """
        token = self.generate_verify_email_token(user, recovery_email)
        link = f'https://anchor-python.teams.hng.tech/dashboard/admin/settings?token={token}'
        
        # Send email in the background
        background_tasks.add_task(
            send_email, 
            recipient=user.email,
            template_name='profile_recovery_email.html',
            subject='Recovery Email Change',
            context={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'link': link
            }
        )

    def update_recovery_email(self, user: User,
                              db: Annotated[Session, Depends(get_db)],
                              token: Token):
        """
        Update user recovery_email.
        Args:
            user: the user object.
            db: database session object
            token: the token retrieved from user(to decode)
        Return:
            response: feedback to the user.
        """
        payload = self.decode_verify_email_token(token.token)
        if payload.get("email") != user.email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid user email')
        profile = db.query(Profile).filter_by(user_id=user.id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User profile not found")
        profile.recovery_email = payload.get("recovery_email")
        db.commit()
                                    
        return ProfileRecoveryEmailResponse(
            message='Recover email successfully updated',
            status_code=status.HTTP_200_OK
        )
        

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
    
    def generate_verify_email_token(self, user: User,
                                    recovery_email: str):
        """
        Generate token for recovery_email.
        Args:
            user: the user object.
            token: the recovery email.
        Return:
            token: token to be sent to the user.
        """
        try:
            now = datetime.now(timezone.utc)
            claims = {
                "iat": now,
                'exp': now + timedelta(minutes=5),
                'recovery_email': recovery_email,
                'email': user.email,
            }
            return jwt.encode(claims=claims, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def decode_verify_email_token(self, token: str):
        """
        decode token for recovery_email.
        Args:
            token: the token retrieved from user(to decode)
        Return:
            payload: the decoded payload/claims.
        """
        try:
            return jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='token expired')


profile_service = ProfileService()
