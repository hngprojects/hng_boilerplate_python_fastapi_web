from fastapi import Depends, status, APIRouter, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, relationship
from api.utils.success_response import success_response
from api.v1.models import User
from typing import Annotated
from datetime import datetime, timedelta

from api.v1.schemas.user import UserCreate
from api.v1.schemas.token import EmailRequest, TokenRequest
from api.utils.email_service import send_mail
from api.db.database import get_db
from api.v1.services.user import user_service

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

