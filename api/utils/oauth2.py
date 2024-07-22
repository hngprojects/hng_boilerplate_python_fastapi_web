from datetime import datetime, timedelta, timezone
from typing import Annotated

from jose import JWTError
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from api.v1.schemas import schemas
from fastapi.security import OAuth2AuthorizationCodeBearer





#SECRET_KEY
#ALGORITHM
#EXPIRATION_TIME

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5

oauth2_scheme =OAuth2PasswordBearer(tokenUrl='/login')


def create_access_token(data: dict):
    to_encode = data.copy()
    # Get the current time in UTC with timezone awareness
    current_time = datetime.now(timezone.utc)
    expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        # id = payload.get("user_id")
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="sorry Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data

# function that get current user by using verify_access_token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )    
    return verify_access_token(token,credentials_exception)
