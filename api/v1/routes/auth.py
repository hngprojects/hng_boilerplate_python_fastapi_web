from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Annotated
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
from api.v1.schemas.token import Token, LoginRequest, TokenResponse
from api.v1.schemas.auth import UserBase, SuccessResponse, SuccessResponseData, UserCreate, ErrorResponse
from api.db.database import get_db
from api.utils.auth import authenticate_user, create_access_token,hash_password,get_user
from api.utils.dependencies import get_current_admin, get_current_user
from fastapi.responses import JSONResponse


from api.v1.models.org import Organization

from api.v1.models.product import Product


db = next(get_db())


auth = APIRouter(prefix="/api/v1/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_EXPIRY = 5

@auth.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
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
    

@auth.post("/login", response_model=TokenResponse)
def login_for_user_info(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        error_response = ErrorResponse(
            message="Login failed",
            error="Incorrect username or password",
            statusCode=status.HTTP_401_UNAUTHORIZED,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict()
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=JWT_REFRESH_EXPIRY)    
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"username": user.username}, expires_delta=refresh_token_expires
    )

    return {
         "message": "Login successful",
        "data": {
            "user": {
                "id": user.id,
                "email": user.email,
                "role": [role.role_name for role in user.roles],
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    }

# Protected route example: test route
@auth.get("/admin")
def read_admin_data(current_admin: Annotated[User, Depends(get_current_admin)]):
    return {"message": "Hello, admin!"}

