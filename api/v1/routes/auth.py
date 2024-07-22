from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from api.v1.models.user import User, WaitlistUser
from api.v1.models.org import Organization
from api.v1.models.profile import Profile
from api.v1.models.product import Product
from api.v1.models.base import Base
from api.v1.models.subscription import Subscription
from api.v1.models.blog import Blog
from api.v1.models.job import Job
from api.v1.models.invitation import Invitation
from api.v1.models.role import Role
from api.v1.models.permission import Permission
from datetime import datetime, timedelta
from api.v1.schemas.token import Token, LoginRequest
from api.v1.schemas.auth import UserBase, SuccessResponse, SuccessResponseData, UserCreate
from api.utils.password_auth import hash_password
from api.db.database import get_db
from api.utils.auth import authenticate_user, create_access_token,hash_password,get_user
from api.utils.dependencies import get_current_admin, get_current_user


from api.v1.models.org import Organization

from api.v1.models.product import Product


db = next(get_db())


auth = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@auth.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login_for_access_token(login_request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    return Token(access_token=access_token, token_type="bearer")
  
@auth.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
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
    try: 
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        print(e)

    user = UserBase(
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        email=db_user.email,
        created_at=datetime.utcnow()
    )
    data = SuccessResponseData(
        token=access_token,
        user=user
    )
    response = SuccessResponse(
        statusCode=201,
        message="Operation successful",
        data=data
    )
    return response
    

# # Protected route example: test route
# @auth.get("/admin")
# def read_admin_data(current_admin: Annotated[User, Depends(get_current_admin)]):
#     return {"message": "Hello, admin!"}

