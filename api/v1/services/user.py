from typing import Any, Optional
import bcrypt, datetime as dt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from api.core.base.services import Service
from api.db.database import get_db
from api.utils.settings import settings
from api.utils.db_validators import check_model_existence
from api.v1.models.user import User
from api.v1.schemas import user

oauth2_scheme = OAuth2PasswordBearer('/api/v1/auth/login')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserService(Service):
    '''User service'''

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all users'''

        query = db.query(User)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(User, column) and value:
                    query = query.filter(getattr(User, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, id):
        '''Fetches a user by their id'''

        user = check_model_existence(db, User, id)
        return user
    
    
    def fetch_by_email(self, db: Session, email):
        '''Fetches a user by their email'''

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        
        return user
    

    def fetch_by_username(self, db: Session, username):
        '''Fetches a user by their username'''

        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        
        return user
    
    
    def create(self, db: Session, schema: user.UserCreate):
        '''Creates a new user'''

        if db.query(User).filter(User.email == schema.email).first() or db.query(User).filter(User.username == schema.username).first():
            raise HTTPException(status_code=400, detail='User with this email or username already exists')

        print(f'PASSWORD: -- {schema.password}')

        # Hash password
        schema.password = self.hash_password(password=schema.password)
        
        # Create user object with hashed password and other attributes from schema
        user = User(**schema.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
    
    
    def update(self, db: Session):
        return super().update()
    
    
    def delete(self, db: Session, id=None, access_token: str = Depends(oauth2_scheme)):
        '''Function to soft delete a user'''
        
        # Get user from access token if provided, otherwise fetch user by id
        user = self.get_current_user(access_token, db) if id is not None else check_model_existence(db, User, id)
        user.is_deleted = True
        db.commit()

        return super().delete()
    

    def authenticate_user(self, db: Session, username: str, password: str):
        '''Function to authenticate a user'''

        user = db.query(User).filter(User.username == username).first()

        if not user:
            raise HTTPException(status_code=400, detail='Invalid user credentials')

        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=400, detail='Invalid user credentials')
        
        return user
    

    def perform_user_check(self, user: User):
        '''This checks if a user is active and verified and not a deleted user'''

        if not user.is_active:
            raise HTTPException(detail='User is not active', status_code=403)
    

    def hash_password(self, password: str) -> str:
        '''Function to hash a password'''
        
        hashed_password = pwd_context.hash(secret=password)     
        return hashed_password


    def verify_password(self, password: str, hash: str) -> bool:
        '''Function to verify a hashed password'''
        
        return pwd_context.verify(secret=password, hash=hash) 
    

    def create_access_token(self, username: str) -> str:
        '''Function to create access token'''
        
        expires = dt.datetime.utcnow() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {
            'username': username,
            'exp': expires,
            'type': 'access'
        }
        
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt


    def create_refresh_token(self, username: str) -> str:
        '''Function to create access token'''
                
        expires = dt.datetime.utcnow() + dt.timedelta(days=settings.JWT_REFRESH_EXPIRY)
        
        data = {
            'username': username,
            'exp': expires,
            'type': 'refresh'
        }
        
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt
    

    def verify_access_token(self, access_token: str, credentials_exception):
        '''Funtcion to decode and verify access token'''
        
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get('username')
            token_type = payload.get('type')
            
            if username is None:
                raise credentials_exception
            
            if token_type == 'refresh':
                raise HTTPException(detail='Refresh token not allowed', status_code=400)
            
            token_data = user.TokenData(id=username)
        
        except JWTError:
            raise credentials_exception
        
        return token_data


    def verify_refresh_token(self, refresh_token: str, credentials_exception):
        '''Funtcion to decode and verify refresh token'''
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get('username')
            token_type = payload.get('type')
            
            if username is None:
                raise credentials_exception
            
            if token_type == 'access':
                raise HTTPException(detail='Access token not allowed', status_code=400)
            
            token_data = user.TokenData(id=username)
        
        except JWTError:
            raise credentials_exception
    
        return token_data
        
        
    def refresh_access_token(self, current_refresh_token: str):
        '''Function to generate new access token and rotate refresh token'''
        
        credentials_exception = HTTPException(
            status_code=401, 
            detail='Refresh token expired'
        )
        
        token = self.verify_refresh_token(current_refresh_token, credentials_exception)
        
        if token:
            access = self.create_access_token(username=token.id)
            refresh = self.create_refresh_token(username=token.id)
            
            return access, refresh
        else:
            pass
    

    def get_current_user(self, access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        '''Function to get current logged in user''' 
        
        credentials_exception = HTTPException(
            status_code=401, 
            detail='Could not validate crenentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        
        token = self.verify_access_token(access_token, credentials_exception)
        user =  db.query(User).filter(User.id == token.id).first()
        
        return user
    

    def deactivate_user(self, request: Request, db: Session, schema: user.DeactivateUserSchema, user: User):
        '''Function to deactivate a user'''

        self.perform_user_check(user)
        user.is_active = False

        # Create reactivation token
        token = self.create_access_token(username=user.id)
        reactivation_link = f'https://{request.url.hostname}/api/v1/users/accounts/reactivate?token={token}'

        # mail_service.send_mail(
        #     to=user.email, 
        #     subject='Account deactivation', 
        #     body=f'Hello, {user.first_name},\n\nYour account has been deactivated successfully.\nTo reactivate your account if this was a mistake, please click the link below:\n{request.url.hostname}/api/users/accounts/reactivate?token={token}\n\nThis link expires after 15 minutes.'
        # )

        db.commit()

        return reactivation_link

    
    def reactivate_user(self, db: Session, token: str):
        '''This function reactivates a user account'''

        # Validate the token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get('username')

            if username is None:
                raise HTTPException(400, 'Invalid token')
            
        except JWTError:
            raise HTTPException(400, 'Invalid token')
        
        user = db.query(User).filter(User.id == username).first()

        if user.is_active:
            raise HTTPException(400, 'User is already active')

        user.is_active = True

        # Send aail to user
        # mail_service.send_mail(
        #     to=user.email, 
        #     subject='Account reactivation', 
        #     body=f'Hello, {user.first_name},\n\nYour account has been reactivated successfully'
        # )

        # Commit changes to deactivate the user
        db.commit()


user_service = UserService()
