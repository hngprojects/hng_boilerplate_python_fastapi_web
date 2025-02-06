from fastapi import BackgroundTasks, Depends, HTTPException
from datetime import datetime, timezone
from api.core.dependencies.email_sender import send_email
from api.db.database import get_db
from api.v1.models.organisation import Organisation
from api.v1.models.oauth import OAuth
from api.v1.models import User, DataPrivacySetting, Region, NewsletterSubscriber
from api.v1.models.profile import Profile
from api.core.base.services import Service
from sqlalchemy.orm import Session
from typing import Annotated, Union
from api.v1.services.user import user_service
from api.v1.schemas.google_oauth import Tokens
from api.v1.services.profile import profile_service
from api.v1.models.associations import user_organisation_association
from api.v1.models.permissions.role_permissions import role_permissions
from api.v1.models.permissions.permissions import Permission
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.services.notification_settings import notification_setting_service
from api.v1.services.newsletter import NewsletterService, EmailSchema


class GoogleOauthServices(Service): 
    """
    Handles database operations for google oauth
    """
    def create(self, background_tasks: BackgroundTasks, google_response: dict, db: Session):
        """
        Creates a user using information from google.

        Args:
            google_response: Raw data from google oauth2
            db: database session to manage database operation

        Returns:
            user: The user object if user already exists or if newly created
            False: for when Authentication fails
        """
        try:
            email = google_response.get("email")
            existing_user = db.query(User).filter_by(email=email).first()

            if existing_user:
                oauth_data = db.query(OAuth).filter_by(user_id=existing_user.id).first()
                if oauth_data:
                    self.update(oauth_data, google_response, db)
                else:
                    self.create_oauth_data(existing_user.id, google_response, db)
                return existing_user
            else:
                new_user = self.create_new_user(google_response, db)
                background_tasks.add_task(
                    send_email, 
                    recipient=new_user.email,
                    template_name='welcome.html',
                    subject='Welcome to HNG Boilerplate',
                    context={
                        'first_name': new_user.first_name,
                        'last_name': new_user.last_name
                    }
                )
                return new_user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f'Error {e}')

    def fetch(self):
        """
        Fetch method
        """
        pass

    def fetch_all(self, db: Annotated[Session, Depends(get_db)]):
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error {e}')
            

    def delete(self):
        """
        Delete method
        """
        pass

    def update(
        self,
        oauth_data: object,
        google_response: dict,
        db: Annotated[Session, Depends(get_db)],
    ):
        """
        Updates a user information in the oauth table

        Args:
            oauth_data: the oauth object
            google_response: the response from google oauth
            db: the database session object for connection

            Returns:
                None: If no exception was raised
                Fasle: if an exception was raised
        """
        try:
            # update the access and refresh token
            oauth_data.access_token = google_response.get("access_token")
            oauth_data.refresh_token = google_response.get("refresh_token", "")
            oauth_data.updated_at = datetime.now(timezone.utc)
            # commit and return the user object
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error {e}')

    def generate_tokens(self, user: object):
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
            tokens = Tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            )
            return tokens
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error {e}')
            

    def create_oauth_data(
        self,
        user_id: int,
        google_response: dict,
        db: Annotated[Session, Depends(get_db)],
    ):
        """
        Creates OAuth data for a new user.

        Args:
            user_id: The ID of the user.
            google_response: The response from Google OAuth.
            db: The database session object for connection.

        Return:
            None: If no exception occured
            False: If an exception occures
        """
        try:
            oauth_data = OAuth(
                provider="google",
                user_id=user_id,
                sub=google_response.get("sub"),
                access_token=google_response.get("access_token"),
                refresh_token=google_response.get("refresh_token", ""),
            )
            db.add(oauth_data)
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error {e}')

    def create_new_user(
        self, google_response: dict, db: Annotated[Session, Depends(get_db)]
    ):
        """
        Creates a new user and their associated profile and OAuth data.

        Args:
            user_info: User information from Google OAuth.
            google_response: The response from Google OAuth.
            db: The database session object for connection.

        Returns:
            new user: The newly created user object.
            False: If an error occured
        """
        try:
            new_user = User(
                first_name=google_response.get("given_name"),
                last_name=google_response.get("family_name"),
                email=google_response.get("email"),
                avatar_url=google_response.get("picture")
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            profile = Profile(user_id=new_user.id,
                              avatar_url=google_response.get("picture"))
            db.add(profile)
            db.commit()
            db.refresh(profile)

            oauth_data = OAuth(
                provider="google",
                user_id=new_user.id,
                sub=google_response.get("sub")
            )
            db.add(oauth_data)
            db.commit()
            db.refresh(oauth_data)

            organisation = Organisation(
                name = f'{new_user.email} {new_user.last_name} Organisation'
            )

            db.add(organisation)
            db.commit()
            db.refresh(organisation)
            
            region = Region(
                user_id=new_user.id,
                region='Empty'
            )
            db.add(region)
            db.commit()
            db.refresh(region)

            # Create notification settings directly for the user
            notification_setting_service.create(db=db, user=new_user)
            
            
            # create data privacy setting
            data_privacy = DataPrivacySetting(user_id=new_user.id)
            db.add(data_privacy)
            db.commit()
            db.refresh(data_privacy)
            #db.add_all([profile, oauth_data, organisation, region, data_privacy])

            news_letter = db.query(NewsletterSubscriber).filter_by(email=new_user.email)
            if not news_letter:
                news_letter = NewsletterService.create(db, EmailSchema(email=new_user.email))
            
            # TODO: Ensure to update this later
            stmt = user_organisation_association.insert().values(
                user_id=new_user.id, organisation_id=organisation.id, role="owner"
            )
            db.execute(stmt)
            db.commit()         
            return new_user
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Error {e}')
