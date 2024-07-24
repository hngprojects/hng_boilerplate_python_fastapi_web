from fastapi import Depends, HTTPException, status
from datetime import datetime, timezone
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.oauth import OAuth
from api.v1.models.profile import Profile
from api.core.base.services import Service
from sqlalchemy.orm import Session
from typing import Annotated, Union
from api.v1.services.user import user_service
from api.v1.schemas.google_oauth import Tokens, UserData, StatusResponse


class GoogleOauthServices(Service):
    """
    Handles database operations for google oauth
    """
    def create(self, google_response: dict,
               db: Annotated[Session, Depends(get_db)]) -> object:
        """
        Creates a user using information from google.

        Args:
            google_response: Raw data from google oauth2
            db: database session to manage database operation

        Returns:
            user: The user object if already exists or if newly created
            Response: HttpException for when Authentication fails
        """
        try:
            # retrieve the user information
            user_info: dict = google_response.get("userinfo")

            existing_user = db.query(User).filter_by(email=user_info.get("email")).one_or_none()

            if existing_user:
                # retrieve the user's google_access_token
                oauth_data = db.query(OAuth).filter_by(user_id=existing_user.id).one_or_none()
                # if the entry exists
                if oauth_data:
                    # update the oauth data
                    self.update(oauth_data, google_response, db)
                    # pass the user object to get_response method to generate a response object
                    user_response = self.get_response(existing_user)
                    return user_response
                # if the entry does not exist
                else:
                    try:
                        # user used google oauth for the first time, save his info
                        # if the user is not found in the database, add the user oauth2_data
                        oauth_data = OAuth(provider="google",
                                           user_id=existing_user.id,
                                           sub=user_info.get("sub"),
                                           access_token=google_response.get("access_token"),
                                           refresh_token=google_response.get("refresh_token", ''))
                        # add and commit to get the inserted_id
                        db.add(oauth_data)
                        db.commit()
                        # update the user's relationship with oauth
                        existing_user.oauth = oauth_data
                        existing_user.updated_at = datetime.now(timezone.utc)
                        db.commit()
                        # pass the user object to get_response method to generate a response object
                        user_response = self.get_response(existing_user)
                        return user_response
                    except Exception as exc:
                        print('creating new oauth1', exc)
                        db.rollback()
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                try:
                    # if the user is not found in the database, add the user oauth2_data
                    # add the user to the database, and link the user to the associated
                    # oauth_data
                    new_user = User(username=user_info.get("email"),
                                    first_name=user_info.get("given_name"),
                                    last_name=user_info.get("family_name"),
                                    email=user_info.get("email"))
                    # commit to get the user_id
                    db.add(new_user)
                    db.commit()
                    
                    oauth_data = OAuth(provider="google",
                                       user_id=new_user.id,
                                       sub=user_info.get("sub"),
                                       access_token=google_response.get("access_token"),
                                       refresh_token=google_response.get("refresh_token", ""))
                    # add and commit to get the inserted_id
                    # add the avatar_url of the new user to the profile
                    profile = Profile(user_id=new_user.id,
                                    avatar_url=user_info.get("picture"))

                    # commit to the database
                    db.add_all([oauth_data, profile])
                    db.commit()
                except Exception as exc:
                    print('creating new oauth2: ', exc)
                    db.rollback()
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

                db.refresh(new_user)

                # pass the user object to get_response method to generate a response object
                user_response = self.get_response(new_user)

                # return the user object for further processing
                return user_response
        except Exception as exc:
            print('create method: ', exc)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def fetch(self):
        """
        Fetch method
        """
        pass

    def fetch_all(self, db: Annotated[Session, Depends(get_db)])-> Union[list, HTTPException]:
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
        except Exception as exc:
            print(exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self):
        """
        Delete method
        """
        pass

    def update(self, oauth_data: object, google_response,
               db: Annotated[Session, Depends(get_db)]) -> None:
        """
        Updates a user information in the oauth table
        
        Args:
            oauth_data: the oauth object
            google_response: the response from google oauth
            db: the database session object for connection
        
            Returns:
                None
        """
        try:
            # update the access and refresh token
            oauth_data.access_token = google_response.get("access_token")
            oauth_data.refresh_token = google_response.get("refresh_token", '')
            oauth_data.updated_at = datetime.now(timezone.utc)
            # commit and return the user object
            db.commit()
        except Exception as exc:
            db.rollback()
            print('update method: ', exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_response(self, user: object) -> object:
        """
        Creates a resnpose for the end user
        
        Args:
            user: the user object
        Returns:
            the response object for the end user
        """
        try:
            # create a user data for response
            user_response = UserData.model_validate(user, strict=True, from_attributes=True)
            # create access token
            access_token = user_service.create_access_token(user.id)
            # create refresh token
            refresh_token = user_service.create_access_token(user.id)
            # create a token data for response
            tokens = Tokens(access_token=access_token,
                            refresh_token=refresh_token,
                            token_type="bearer")

            success_response = StatusResponse(message="Authentication was successful",
                                              status="successful",
                                              statusCode=200,
                                              tokens=tokens,
                                              user=user_response)
            return success_response
        except Exception as exc:
            print('error in get_response: ', exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
