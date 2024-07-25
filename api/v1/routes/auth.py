from fastapi import Depends, status, APIRouter, Response, Request, HTTPException

from fastapi import Depends, status, APIRouter, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, relationship
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated, Optional
from datetime import datetime, timedelta

from api.v1.schemas.user import UserCreate
from api.v1.schemas.token import EmailRequest, TokenRequest
from api.utils.email_service import send_mail
from api.db.database import get_db
from api.v1.services.user import user_service

# from fastapi import BackgroundTasks
# from fastapi_mail import ConnectionConfig
from pydantic import BaseModel, EmailStr
from api.utils.settings import settings, BASE_DIR
import uuid
import jwt
from urllib.parse import urlencode

auth = APIRouter(prefix="/auth", tags=["Authentication"])

@auth.post("/login", status_code=status.HTTP_200_OK)
def login(login_request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    '''Endpoint to log in a user'''

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db,
        username=login_request.username,
        password=login_request.password
    )

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = success_response(
        status_code=200,
        message='Login successful',
        data={
            'access_token': access_token,
            'token_type': 'bearer',
        }
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response



@auth.post("/register", status_code=status.HTTP_201_CREATED)
def register(response: Response, user_schema: UserCreate, db: Session = Depends(get_db)):
    '''Endpoint for a user to register their account'''

    # Create user account
    user = user_service.create(db=db, schema=user_schema)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = success_response(
        status_code=201,
        message='User created successfully',
        data={
            'access_token': access_token,
            'token_type': 'bearer',
            'user': user.to_dict()
        }
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=60),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response


@auth.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to log a user out of their account'''

    response = success_response(
        status_code=200,
        message='User logged put successfully'
    )

    # Delete refresh token from cookies
    response.delete_cookie(key='refresh_token')

    return response


@auth.post("/refresh-access-token", status_code=status.HTTP_200_OK)
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    '''Endpoint to log a user out of their account'''

    # Get refresh token
    current_refresh_token = request.cookies.get('refresh_token')

    # Create new access and refresh tokens
    access_token, refresh_token = user_service.refresh_access_token(current_refresh_token=current_refresh_token)

    response = success_response(
        status_code=200,
        message='Tokens refreshed cuccessfully',
        data={
            'access_token': access_token,
            'token_type': 'bearer',
        }
    )

    # Add refresh token to cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        expires=timedelta(days=30),
        httponly=True,
        secure=True,
        samesite="none",
    )

    return response

@auth.post("/request-token", status_code=status.HTTP_200_OK)
async def request_signin_token(email_schema: EmailRequest, db: Session = Depends(get_db)):
    '''Generate and send a 6-digit sign-in token to the user's email'''

    user = user_service.fetch_by_email(db, email_schema.email)

    token, token_expiry = user_service.generate_token()

    # Save the token and expiry
    user_service.save_login_token(db, user, token, token_expiry)

    # Send the token to the user's email
    # send_mail(to=user.email, subject="Your SignIn Token", body=token)

    return success_response(
        status_code=200,
        message="Sign-in token sent to email"
    )

@auth.post("/verify-token", status_code=status.HTTP_200_OK)
async def verify_signin_token(token_schema: TokenRequest, db: Session = Depends(get_db)):
    '''Verify the 6-digit sign-in token and log in the user'''

    user = user_service.verify_login_token(db, schema=token_schema)

    # Generate JWT token
    access_token = user_service.create_access_token(user_id=user.id)

    return success_response(
        status_code=200,
        message="Sign-in successful",
        data={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


# Protected route example: test route
@auth.get("/admin")
def read_admin_data(current_admin: Annotated[User, Depends(user_service.get_current_super_admin)]):
    return {"message": "Hello, admin!"}

def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_password_reset_token(user_id: uuid, generate_access_token) -> str:
    expires_delta = timedelta(minutes=30)
    data = {"sub": str(user_id)}
    return generate_access_token(data=data, expires_delta=expires_delta)


def generate_reset_password_url(user_id: uuid, token: str) -> str:
    base_url = f"http://localhost:7001"
    path = "/reset-password"
    query_params = urlencode({"token": token, "user_id": str(user_id)})
    return f"{base_url}{path}?{query_params}"


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


class EmailRequest(BaseModel):
    email: EmailStr


@auth.post("/password-reset-email/", status_code=status.HTTP_200_OK)
async def send_reset_password_email(email: EmailRequest, db: Session = Depends(get_db)):
    """
    Getting the user from the database, the email in the db since the email schema in the db is unique, it picks the 1st
    """

    # user = get_user_by_email(db, email.email)
    user = get_user_by_email(db, email.email)
    if not user:
        raise HTTPException(status_code=404, detail="We don't have user with the provided email in our database.")
    # Generate password reset token
    password_reset_token = generate_password_reset_token(user_id=user.id, generate_access_token=generate_access_token)
    reset_password_url = generate_reset_password_url(user_id=user.id, token=password_reset_token)

    email_body = (f"Dear {user.username}!\nYou requested for email reset on our site.\n"
                  f"To reset your password, click the following link: {reset_password_url}")
    try:
        send_mail(to=email.email, subject="Reset Password", body=email_body)
        return {
            "message": "Password reset email sent successfully.",
            "reset_link": reset_password_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e}")