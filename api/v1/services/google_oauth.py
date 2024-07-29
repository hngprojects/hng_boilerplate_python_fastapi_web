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
from api.v1.schemas.google_oauth import Tokens


CLIENT_ID = config('GOOGLE_CLIENT_ID')

class GoogleOauthServices(Service):
    """
    Handles database operations for google oauth
    """
    async def verify_google_token(self, token: str):
        """
        Verifies id_token
        Args:
            id_token: the id_token to verify
        Returns:
            Exception: if error occurs
            Tokens: if authenticated
        """
        try:
            print('id_token: ', token)
            # Verify the token
            id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            print('after id_info verification: ', id_info)
            
            user = self.create(id_info)
            print('user: ', user)
            
            if not user:
                return False
            tokens = await self.generate_tokens(user)
            print('tokens: ', tokens)
            
            return token
        except (GoogleAuthError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def create(self, info: dict,
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
            user = User(email=info['email'], first_name=info['name'])
            
            db.add(user)
            db.commit()
            oauth = OAuth(sub=info['sub'], access_token='None', refresh_token='None')
            profile = Profile(user_id=user.id)
            
            db.add_all([oauth, profile])
            db.commit()
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
            # create a token data for response
            tokens = Tokens(access_token=access_token,
                            refresh_token=refresh_token)
            return tokens
        except Exception:
            return False

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