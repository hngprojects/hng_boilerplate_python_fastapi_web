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

        username = payload.get("username")
        user_id = payload.get("user_id")
        
        if username is None and user_id is None:
            raise credentials_exception
        
        if username:
            token_data = TokenData(username=username)
        else:
            token_data = TokenData(user_id=user_id)

    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception
    
    if token_data.username:
        user = db.query(User).filter(User.username == token_data.username).first()
    else:
        user = db.query(User).filter(User.id == token_data.user_id).first()

    if user is None:
        raise credentials_exception

    return user