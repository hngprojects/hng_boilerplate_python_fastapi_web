from datetime import timedelta
from fastapi import BackgroundTasks, Depends, status, APIRouter, Response, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.core.dependencies.email_sender import send_email
from api.utils.success_response import auth_response, success_response
from api.utils.send_mail import send_magic_link
from api.v1.models import User
from api.v1.schemas.user import Token
from api.v1.schemas.user import LoginRequest, UserCreate, EmailRequest
from api.v1.schemas.token import TokenRequest
from api.v1.schemas.user import UserCreate, MagicLinkRequest, ChangePasswordSchema
from api.v1.services.organisation import organisation_service
from api.v1.schemas.organisation import CreateUpdateOrganisation
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.auth import AuthService

auth = APIRouter(prefix="/auth", tags=["Authentication"])

  
@auth.post("/register", status_code=status.HTTP_201_CREATED, response_model=auth_response)
def register(background_tasks: BackgroundTasks, response: Response, user_schema: UserCreate, db: Session = Depends(get_db)):
    '''Endpoint for a user to register their account'''

    # Create user account
    user = user_service.create(db=db, schema=user_schema)

    # create an organization for the user
    org = CreateUpdateOrganisation(
        name=f"{user.email}'s Organisation",
        email=user.email
    )
    user_org = organisation_service.create(db=db, schema=org, user=user)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    # Send email in the background
    background_tasks.add_task(
        send_email, 
        recipient=user.email,
        template_name='welcome.html',
        subject='Welcome to HNG Boilerplate',
        context={
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    )

    response = auth_response(
        status_code=201,
        message='User created successfully',
        access_token=access_token,
        data={
            'user': jsonable_encoder(
                user,
                exclude=['password', 'is_deleted', 'is_verified', 'updated_at']
            )
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


@auth.post(path="/register-super-admin", status_code=status.HTTP_201_CREATED, response_model=auth_response)
def register_as_super_admin(user: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for super admin creation"""

    user = user_service.create_admin(db=db, schema=user)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=201,
        message='User created successfully',
        access_token=access_token,
        data={
            'user': jsonable_encoder(
                user,
                exclude=['password', 'is_deleted', 'is_verified', 'updated_at']
            )
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


@auth.post("/login", status_code=status.HTTP_200_OK, response_model=auth_response)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Endpoint to log in a user"""

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=200,
        message='Login successful',
        access_token=access_token,
        data={
            'user': jsonable_encoder(
                user,
                exclude=['password', 'is_deleted', 'is_verified', 'updated_at']
            )
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


@auth.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to log a user out of their account"""

    response = success_response(status_code=200, message="User logged put successfully")

    # Delete refresh token from cookies
    response.delete_cookie(key="refresh_token")

    return response


@auth.post("/refresh-access-token", status_code=status.HTTP_200_OK)
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """Endpoint to log a user out of their account"""

    # Get refresh token
    current_refresh_token = request.cookies.get("refresh_token")

    # Create new access and refresh tokens
    access_token, refresh_token = user_service.refresh_access_token(
        current_refresh_token=current_refresh_token
    )

    response = auth_response(
        status_code=200,
        message='Login successful',
        access_token=access_token
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
async def request_signin_token(
    email_schema: EmailRequest, db: Session = Depends(get_db)
):
    """Generate and send a 6-digit sign-in token to the user's email"""

    user = user_service.fetch_by_email(db, email_schema.email)

    token, token_expiry = user_service.generate_token()

    # Save the token and expiry
    user_service.save_login_token(db, user, token, token_expiry)

    # Send mail notification

    return success_response(
        status_code=200, message=f"Sign-in token sent to {user.email}"
    )


@auth.post("/verify-token", status_code=status.HTTP_200_OK, response_model=auth_response)
async def verify_signin_token(
    token_schema: TokenRequest, db: Session = Depends(get_db)
):
    """Verify the 6-digit sign-in token and log in the user"""

    user = user_service.verify_login_token(db, schema=token_schema)

    # Generate JWT token
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)


    response = auth_response(
        status_code=200,
        message='Login successful',
        access_token=access_token,
        data={
            'user': jsonable_encoder(
                user,
                exclude=['password', 'is_deleted', 'is_verified', 'updated_at']
            )
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


# TODO: Fix magic link authentication
@auth.post("/magic-link", status_code=status.HTTP_200_OK)
def request_magic_link(
    request: MagicLinkRequest, response: Response, db: Session = Depends(get_db)
):
    user = user_service.fetch_by_email(db=db, email=request.email)
    access_token = user_service.create_access_token(user_id=user.id)
    send_magic_link(user.email, access_token)

    response = success_response(
        status_code=200, message=f"Magic link sent to {user.email}"
    )
    return response


@auth.post("/magic-link/verify")
async def verify_magic_link(token_schema: Token, db: Session = Depends(get_db)):
    user, access_token = AuthService.verify_magic_token(token_schema.access_token, db)

    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=200,
        message='Login successful',
        access_token=access_token,
        data={
            'user': jsonable_encoder(
                user,
                exclude=['password', 'is_deleted', 'is_verified', 'updated_at']
            )
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

@auth.patch("/change-password", status_code=200)
async def change_password(
    schema: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    """Endpoint to change the user's password"""
    user_service.change_password(new_password=schema.new_password,
                                 user=user,
                                 db=db,
                                 old_password=schema.old_password)

    return success_response(status_code=200, message="Password changed successfully")