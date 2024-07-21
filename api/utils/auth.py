from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated
import jwt
from typing import Optional
from datetime import datetime, timedelta
from api.v1.models.user import User
from api.v1.models.profile import Profile
from api.v1.models.oauth2_data import Oauth2_data
import os
from jose import JWTError
import bcrypt
from api.v1.schemas.token import TokenData
from api.db.database import get_db
from .config import SECRET_KEY, ALGORITHM

# Initialize OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user_from_google_info(google_response: dict,
                                 db: Annotated[Session, Depends(get_db)]) -> Optional[object]:
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
        # get the access_token from response
        google_access_token = google_response.get("access_token")
        google_refresh_token = google_response.get("refresh_token", '')

        if not google_access_token:
            raise HTTPException(status_code=400, detail="Authentication Failed")
        # retrieve the user information
        user_info: dict = google_response.get("userinfo")

        email = user_info.get("email")
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")
        avatar_url = user_info.get("picture")
        sub_identifier = user_info.get("sub")


        existing_user = db.query(User).filter_by(email=email).one_or_none()

        if existing_user:
            # retrieve and update the user's google_access_token
            oauth2_data = db.query(Oauth2_data).filter_by(id=existing_user.oauth2_data_id)
            # update the access and refresh token
            oauth2_data.access_token = google_access_token
            oauth2_data.refresh_token = google_refresh_token
            # commit and return the user object
            db.commit()
            return existing_user
        else:
            # if the user is not found in the database, add the user oauth2_data
            oauth2_data = Oauth2_data(oauth2_provider="google",
                                      sub=sub_identifier,
                                      access_token=google_access_token,
                                      refresh_token=google_refresh_token)
            # add and commit to get the inserted_id
            db.add(oauth2_data)
            db.commit()

            # add the user to the database, and link the user to the associated
            # oauth2_data
            new_user = User(username=email,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            oauth2_data_id=oauth2_data.id)
            # commit to get the user_id
            db.add(new_user)
            db.commit()

            # add the avatar_url of the new user to the profile
            profile = Profile(user_id=new_user.id,
                              avatar_url=avatar_url)

            # commit to the database
            db.add(profile)
            db.commit()
            db.refresh(new_user)
            # return the user object for further processing
            return new_user
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal Server Error")
