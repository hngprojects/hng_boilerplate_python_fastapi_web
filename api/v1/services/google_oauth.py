from fastapi import (Depends, status, HTTPException)
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from decouple import config


from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.oauth import OAuth
from api.v1.models.profile import Profile
from api.core.base.services import Service
from sqlalchemy.orm import Session
from typing import Annotated, Union
from api.v1.services.user import user_service


CLIENT_ID = config('GOOGLE_CLIENT_ID')

class GoogleOauthServices(Service):
    """
    Handles database operations for google oauth
    """
    def verify_google_token(self, token: str,
                                  db: Annotated[Session, Depends(get_db)]):
        """
        Verifies id_token
        Args:
            id_token: the id_token to verify
        Returns:
            Exception: if error occurs
            Tokens: if authenticated
        """
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            
            user = self.create(id_info, db)
            
            if not user:
                return False, False
            access, refresh = self.generate_tokens(user)
            
            return access, refresh
        except (GoogleAuthError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def create(self, info: dict,
               db: Annotated[Session, Depends(get_db)]) -> object:
        """
        Creates a user using information from google.

        Args:
            google_response: Raw data from google oauth2
            db: database session to manage database operation

        Returns:
            user: The token object if user already exists or if newly created
            False: for when Authentication fails
        """
        try:
            user_exists = db.query(User).filter_by(email=info['email']).one_or_none()
            if user_exists:
                return user_exists
            user = User(email=info['email'], first_name=info['given_name'],
                        last_name=info['family_name'])
            
            db.add(user)
            db.commit()
            oauth = OAuth(user_id=user.id, provider='google',
                          sub=info['sub'], access_token='None', refresh_token='None')
            profile = Profile(user_id=user.id, avatar_url=info['picture'])
            
            db.add_all([oauth, profile])
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            return False
    
    def generate_tokens(self, user: object) -> Union[object, bool]:
        """
        Creates a resnpose for the end user

        Args:
            user: the user object
        Returns:
            tokens: the object containing access and refresh tokens for the user
        """
        try:
            # create access token
            access_token = user_service.create_access_token(user.id)
            # create refresh token
            refresh_token = user_service.create_access_token(user.id)
            
            return access_token, refresh_token
        except Exception:
            return False, False

    def fetch(self):
        """
        Fetch method
        """
        pass

    def fetch_all(self, db: Annotated[Session, Depends(get_db)])-> Union[list, bool]:
        """
        Retrieves all users information from the oauth table

        Args:
            db: the database session object for connection

            Returns:
                list: a list containing all data in oauth table
        """
        try:
            all_oauth = db.query(OAuth).all()
            return all_oauth
        except Exception:
            return False

    def delete(self):
        """
        Delete method
        """
        pass
    
    def update(self):
        pass