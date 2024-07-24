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
from .config import SECRET_KEY, ALGORITHM
from urllib.parse import urlencode
import uuid

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


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def generate_password_reset_token(user_id: uuid.UUID) -> str:
    expires_delta = timedelta(minutes=30)
    data = {"sub": user_id}
    return create_access_token(data=data, expires_delta=expires_delta)


def generate_reset_password_url(user_id: uuid.UUID, token: str) -> str:
    base_url = f"http://localhost:7001"
    path = "/reset-password"
    query_params = urlencode({"token": token, "user_id": user_id})
    return f"{base_url}{path}?{query_params}"
