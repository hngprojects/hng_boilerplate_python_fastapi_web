from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from typing import Optional
from datetime import datetime, timedelta
from api.v1.models.user import User
import os
from jose import JWTError
import bcrypt
from api.v1.schemas.token import TokenData
from api.db.database import get_db
from api.utils.config import SECRET_KEY, ALGORITHM


# Initialize OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"Token received: {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded Payload: {payload}")
        user_id: str = payload.get("user_id")  # Change this to user_id
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)  # Adjust the TokenData to use user_id
    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception
    user = db.query(User).filter(User.id == token_data.user_id).first()  # Query by user_id
    if user is None:
        raise credentials_exception
    return user



def get_super_admin(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(db, token)
    if not user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return user

