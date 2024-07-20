from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..models.user import User
from ..models.profile import Profile
from datetime import datetime, timedelta
from api.v1.schemas.token import Token, LoginRequest
from api.v1.schemas.auth import UserCreate
from api.utils import json_response
from api.db.database import get_db
from api.utils.auth import authenticate_user, create_access_token, get_current_admin, get_current_user,hash_password,get_user


from api.v1.models.org import Organization

from api.v1.models.product import Product


db = next(get_db())


router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/login", response_model=Token)
def login_for_access_token(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
  
@router.post("/register", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    password_hashed = hash_password(user.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )

    db_user = User(
        username=user.username,
        email=user.email,
        password = password_hashed,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    # user_response = UserResponse.from_orm(db_user)
    # user = user_response.dict()
    # return {
    #         "statusCode": 201,
    #         "message": "User regisitration successful",
    #         "data" : {
    #                 "token": access_token,
    #                 "user": {
    #                 "id": user.id,
    #                 "first_name": user.first_name,
    #                 "last_name": user.last_name,
    #                 "email": user.email,
    #                 "created_at": user.create_at
    #             },
    #         }
    #     }

    

# Protected route example: test route
@router.get("/admin")
def read_admin_data(current_admin: User = Depends(get_current_admin)):
    return {"message": "Hello, admin!"}

#protected route
@router.get("/test")
def test(user: User = Depends(get_current_user)):
    return {f"message": "Hello, welcome {user.username}"}