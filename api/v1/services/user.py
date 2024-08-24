import random
import string
from typing import Any, Optional, Annotated
import datetime as dt
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.context import CryptContext
from datetime import datetime, timedelta

from api.core.base.services import Service
from api.core.dependencies.email_sender import send_email
from api.db.database import get_db
from api.utils.settings import settings
from api.utils.db_validators import check_model_existence
from api.v1.models.associations import user_organisation_association
from api.v1.models import User, Profile, Region, NewsletterSubscriber
from api.v1.models.data_privacy import DataPrivacySetting
from api.v1.models.token_login import TokenLogin
from api.v1.schemas import user
from api.v1.schemas import token
from api.v1.services.notification_settings import notification_setting_service
from api.v1.services.newsletter import NewsletterService, EmailSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(Service):
    """User service"""

    def fetch_all(
        self, db: Session, page: int, per_page: int, **query_params: Optional[Any]
    ):
        """
        Fetch all users
        Args:
            db: database Session object
            page: page number
            per_page: max number of users in a page
            query_params: params to filter by
        """
        per_page = min(per_page, 10)

        # Enable filter by query parameter
        filters = []
        if all(query_params):
            # Validate boolean query parameters
            for param, value in query_params.items():
                if value is not None and not isinstance(value, bool):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Invalid value for '{param}'. Must be a boolean.",
                    )
                if value == None:
                    continue
                if hasattr(User, param):
                    filters.append(getattr(User, param) == value)
        query = db.query(User)
        total_users = query.count()
        if filters:
            query = query.filter(*filters)
            total_users = query.count()

        all_users: list = (
            query.order_by(desc(User.created_at))
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )

        return self.all_users_response(all_users, total_users, page, per_page)

    def all_users_response(
        self, users: list, total_users: int, page: int, per_page: int
    ):
        """
        Generates a response for all users
        Args:
            users: a list containing user objects
            total_users: total number of users
        """
        if not users or len(users) == 0:
            return user.AllUsersResponse(
                message="No User(s) for this query",
                status="success",
                status_code=200,
                page=page,
                per_page=per_page,
                total=0,
                data=[],
            )
        all_users = [
            user.UserData.model_validate(usr, from_attributes=True) for usr in users
        ]
        return user.AllUsersResponse(
            message="Users successfully retrieved",
            status="success",
            status_code=200,
            page=page,
            per_page=per_page,
            total=total_users,
            data=all_users,
        )

    def fetch(self, db: Session, id):
        """Fetches a user by their id"""

        user = check_model_existence(db, User, id)

        # return user if user is not deleted
        if not user.is_deleted:
            return user

    def get_user_by_id(self, db: Session, id: str):
        """Fetches a user by their id"""

        user = check_model_existence(db, User, id)
        return user
    
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Fetches a user by their email address.

        Args:
            db: The database session.
            email: The email address of the user.

        Returns:
            The user object if found, otherwise None.
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return user
    
    def fetch_by_email(self, db: Session, email):
        """Fetches a user by their email"""

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    def create(self, db: Session, schema: user.UserCreate):
        """Creates a new user"""

        if db.query(User).filter(User.email == schema.email).first():
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Hash password
        schema.password = self.hash_password(password=schema.password)

        # Create user object with hashed password and other attributes from schema
        user = User(**schema.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)

        # # Create notification settings directly for the user
        notification_setting_service.create(db=db, user=user)

        # create data privacy setting
        data_privacy = DataPrivacySetting(user_id=user.id)
        profile = Profile(
            user_id=user.id
        )
        region = Region(
            user_id=user.id,
            region='Empty'
        )
        
        news_letter = db.query(NewsletterSubscriber).filter_by(email=user.email)
        if not news_letter:
            news_letter = NewsletterService.create(db, EmailSchema(email=user.email))

        db.add_all([data_privacy, profile, region])
        db.commit()
        db.refresh(data_privacy)

        return user

    def super_admin_create_user(
        self,
        db: Annotated[Session, Depends(get_db)],
        user_request: user.AdminCreateUser,
    ):
        """
        Creates a user for super admin
        Args:
            db: database Session object
            user_request: The user details to use for creation
        Returns:
            object: the complete details of the newly created user
        """
        try:
            user_exists = (
                db.query(User).filter_by(email=user_request.email).one_or_none()
            )
            if user_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with {user_request.email} already exists",
                )
            if user_request.password:
                user_request.password = self.hash_password(user_request.password)
            new_user = User(**user_request.model_dump())
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create notification settings directly for the user
            notification_setting_service.create(db=db, user=new_user)

            # create data privacy setting
            data_privacy = DataPrivacySetting(user_id=new_user.id)
            profile = Profile(
                user_id=new_user.id
            )
            region = Region(
                user_id=new_user.id,
                region='Empty'
            )

            db.add_all([data_privacy, profile, region])
            db.commit()

            user_schema = user.UserData.model_validate(new_user, from_attributes=True)
            return user.AdminCreateUserResponse(
                message="User created successfully",
                status_code=201,
                status="success",
                data=user_schema,
            )
        except Exception as exc:
            db.rollback()
            raise Exception(exc) from exc

    def create_admin(self, db: Session, schema: user.UserCreate):
        """Creates a new admin"""

        if db.query(User).filter(User.email == schema.email).first():
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Hash password
        schema.password = self.hash_password(password=schema.password)

        # Create user object with hashed password and other attributes from schema
        user = User(**schema.model_dump())

        user.is_superadmin = True
        db.add(user)
        db.commit()

        # # Create notification settings directly for the user
        notification_setting_service.create(db=db, user=user)

        # create data privacy setting
        data_privacy = DataPrivacySetting(user_id=user.id)
        profile = Profile(
            user_id=user.id
        )
        region = Region(
            user_id=user.id,
            region='Empty'
        )

        db.add_all([data_privacy, profile, region])
        db.commit()

        db.refresh(user)

        return user

    def update(self, db: Session, current_user: User, schema: user.UserUpdate, id=None):
        """Function to update a User"""
        
        # Get user from access token if provided, otherwise fetch user by id
        user = (self.fetch(db=db, id=id) 
                if current_user.is_superadmin and id is not None
                else self.fetch(db=db, id=current_user.id)
            )
        
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'email':
                continue
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, id=None, access_token: str = Depends(oauth2_scheme)):
        """Function to soft delete a user"""

        # Get user from access token if provided, otherwise fetch user by id
        user = (
            self.get_current_user(access_token, db)
            if id is None
            else check_model_existence(db, User, id)
        )

        user.is_deleted = True
        db.commit()

        return super().delete()

    def authenticate_user(self, db: Session, email: str, password: str):
        """Function to authenticate a user"""

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        return user

    def perform_user_check(self, user: User):
        """This checks if a user is active and verified and not a deleted user"""

        if not user.is_active:
            raise HTTPException(detail="User is not active", status_code=403)

    def hash_password(self, password: str) -> str:
        """Function to hash a password"""

        hashed_password = pwd_context.hash(secret=password)
        return hashed_password

    def verify_password(self, password: str, hash: str) -> bool:
        """Function to verify a hashed password"""

        return pwd_context.verify(secret=password, hash=hash)

    def create_access_token(self, user_id: str) -> str:
        """Function to create access token"""

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {"user_id": user_id, "exp": expires, "type": "access"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, user_id: str) -> str:
        """Function to create access token"""

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            days=settings.JWT_REFRESH_EXPIRY
        )
        data = {"user_id": user_id, "exp": expires, "type": "refresh"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    def verify_access_token(self, access_token: str, credentials_exception):
        """Funtcion to decode and verify access token"""

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if user_id is None:
                raise credentials_exception

            if token_type == "refresh":
                raise HTTPException(detail="Refresh token not allowed", status_code=400)

            token_data = user.TokenData(id=user_id)

        except JWTError as err:
            print(err)
            raise credentials_exception

        return token_data

    def verify_refresh_token(self, refresh_token: str, credentials_exception):
        """Funtcion to decode and verify refresh token"""

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("user_id")
            token_type = payload.get("type")

            if user_id is None:
                raise credentials_exception

            if token_type == "access":
                raise HTTPException(detail="Access token not allowed", status_code=400)

            token_data = user.TokenData(id=user_id)

        except JWTError:
            raise credentials_exception

        return token_data

    def refresh_access_token(self, current_refresh_token: str):
        """Function to generate new access token and rotate refresh token"""

        credentials_exception = HTTPException(
            status_code=401, detail="Refresh token expired"
        )

        token = self.verify_refresh_token(current_refresh_token, credentials_exception)

        if token:
            access = self.create_access_token(user_id=token.id)
            refresh = self.create_refresh_token(user_id=token.id)

            return access, refresh

    def get_current_user(
        self, access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ) -> User:
        """Function to get current logged in user"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token = self.verify_access_token(access_token, credentials_exception)
        user = db.query(User).filter(User.id == token.id).first()

        return user

    def deactivate_user(
        self,
        request: Request,
        db: Session,
        schema: user.DeactivateUserSchema,
        user: User,
    ):
        """Function to deactivate a user"""

        if not schema.confirmation:
            raise HTTPException(
                detail="Confirmation required to deactivate account", status_code=400
            )

        self.perform_user_check(user)

        user.is_active = False

        # Create reactivation token
        token = self.create_access_token(user_id=user.id)
        reactivation_link = f"https://{request.url.hostname}/api/v1/users/accounts/reactivate?token={token}"

        # mail_service.send_mail(
        #     to=user.email,
        #     subject='Account deactivation',
        #     body=f'Hello, {user.first_name},\n\nYour account has been deactivated successfully.\nTo reactivate your account if this was a mistake, please click the link below:\n{request.url.hostname}/api/users/accounts/reactivate?token={token}\n\nThis link expires after 15 minutes.'
        # )

        db.commit()

        return reactivation_link

    def reactivate_user(self, db: Session, token: str):
        """This function reactivates a user account"""

        # Validate the token
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("user_id")

            if user_id is None:
                raise HTTPException(400, "Invalid token")

        except JWTError:
            raise HTTPException(400, "Invalid token")

        user = db.query(User).filter(User.id == user_id).first()

        if user.is_active:
            raise HTTPException(400, "User is already active")

        user.is_active = True

        db.commit()

    def change_password(
        self,
        new_password: str,
        user: User,
        db: Session,
        old_password: Optional[str] = None
    ):
        """Endpoint to change the user's password"""
        if old_password == new_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Old Password and New Password cannot be the same")
        if old_password is None:
            if user.password is None:
                user.password = self.hash_password(new_password)
                db.commit()
                return
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Old Password must not be empty, unless setting password for the first time.")
        elif not self.verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect old password")
        else:
            user.password = self.hash_password(new_password)
            db.commit()

    def get_current_super_admin(
        self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
    ):
        """Get the current super admin"""
        user = self.get_current_user(db=db, access_token=token)
        if not user.is_superadmin:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        return user

    def save_login_token(
        self, db: Session, user: User, token: str, expiration: datetime
    ):
        """Save the token and expiration in the user's record"""
        db.query(TokenLogin).filter_by(user_id=user.id).delete(synchronize_session='fetch')
        token = TokenLogin(user_id=user.id, token=token, expiry_time=expiration)
        db.add(token)
        db.commit()

    def verify_login_token(self, db: Session, schema: token.TokenRequest):
        """Verify the token and email combination"""
        token = db.query(TokenLogin).filter_by(token=schema.token).first()
        if not token:
            raise HTTPException(status_code=404, detail="Token Expired")

        if token.token != schema.token or token.expiry_time < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid email or token")

        db.delete(token)
        db.commit()

        return db.query(User).filter_by(id=token.user_id).first()

    def generate_token(self):
        """Generate a 6-digit token"""
        return "".join(
            random.choices(string.digits, k=6)
        ), datetime.utcnow() + timedelta(minutes=1)


    def get_users_by_role(self, db: Session, role_id: str, current_user: User):
        """Function to get all users by role"""
        if role_id == "" or role_id is None:
            raise HTTPException(
                status_code=400, 
                detail="Role ID is required"
            )

        user_roles = db.query(user_organisation_association).filter(user_organisation_association.c.user_id == current_user.id, user_organisation_association.c.role.in_(['admin', 'owner'])).all()

        if len(user_roles) == 0:
            raise HTTPException(
                status_code=403, 
                detail="Permission denied. Admin access required."
            )

        users = db.query(User).join(user_organisation_association).filter(user_organisation_association.c.role == role_id).all()

        if len(users) == 0:
            raise HTTPException(
                status_code=404, 
                detail="No users found for this role"
            )

        return users

user_service = UserService()
