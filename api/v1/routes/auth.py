import logging
from datetime import timedelta
from fastapi.responses import JSONResponse
from jose import ExpiredSignatureError, JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi import BackgroundTasks, Depends, status, APIRouter, Response, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Annotated

from api.core.dependencies.email_sender import send_email
from api.utils.success_response import auth_response, success_response
from api.utils.send_mail import send_magic_link
from api.v1.models import User
from api.v1.schemas.user import Token, UserEmailSender
from api.v1.schemas.user import (
    LoginRequest,
    UserCreate,
    EmailRequest,
    ProfileData,
    UserData2,
)
from api.v1.schemas.token import TokenRequest
from api.v1.schemas.user import (MagicLinkRequest,
                                 ChangePasswordSchema,
                                 AuthMeResponse)
from api.v1.services.login_notification import send_login_notification
from api.v1.services.organisation import organisation_service
from api.v1.schemas.organisation import CreateUpdateOrganisation
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.services.auth import AuthService
from api.v1.services.profile import profile_service
from api.v1.schemas.totp_device import TOTPDeviceRequestSchema, TOTPDeviceResponseSchema, TOTPTokenSchema, TOTPDeviceDataSchema
from api.v1.services.totp import totp_service
from api.utils.settings import settings

auth = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  
@auth.post("/register", status_code=status.HTTP_201_CREATED, response_model=auth_response)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def register(request: Request, background_tasks: BackgroundTasks, response: Response, user_schema: UserCreate, db: Session = Depends(get_db)):
    '''Endpoint for a user to register their account'''

    base_url = str(request.base_url).strip("/")
    # Create user account
    user = user_service.create(db=db, schema=user_schema)


    verification_token = user_service.create_verification_token(user.id)
    verification_link = f"{base_url}/api/v1/auth/verify-email?token={verification_token}"

    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)
    cta_link = "https://anchor-python.teams.hng.tech/about-us"

    # create an organization for the user
    org = CreateUpdateOrganisation(
        name=f"{user.email}'s Organisation", email=user.email
    )
    organisation_service.create(db=db, schema=org, user=user)
    user_organizations = organisation_service.retrieve_user_organizations(user, db)
    
    
    # Send email in the background
    background_tasks.add_task(
        send_email,
        recipient=user.email,
        template_name="welcome.html",
        subject="Welcome to HNG Boilerplate",
        context={
            "first_name": user.first_name,
            "last_name": user.last_name,
            'verification_link': verification_link,
            "cta_link": cta_link,
        },
    )

    response = auth_response(
        status_code=201,
        message="User created successfully",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "is_verified", "updated_at"]
            ),
            "organisations": user_organizations,
        },
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


@auth.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    '''Endpoint to verify email'''
    try:
        return user_service.verify_user_email(token, db)
    except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification link expired"
            )
        
    except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

@auth.post("/resend_verification_email")
def resend_verification_email(request: Request, data: UserEmailSender, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Resends the email verification link"""
    email = data.email
    print(email)
    user = user_service.user_to_verify(email, db)
    verification_token = user_service.create_verification_token(user.id)
    base_url = str(request.base_url).strip("/")
    verification_link = f"{base_url}/api/v1/auth/verify-email?token={verification_token}"
    cta_link = 'https://anchor-python.teams.hng.tech/about-us'

    background_tasks.add_task(
        send_email,
        recipient=email,
        template_name='welcome.html',
        subject='Welcome to HNG Boilerplate, Verify Your Email below',
        context={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'verification_link': verification_link,
            'cta_link': cta_link
        }
    )

    return {
        "status": "success",
        "status_code": 200,
        "message": "Verification email sent successfully"
    }
 



@auth.post(path="/register-super-admin", status_code=status.HTTP_201_CREATED, response_model=auth_response)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def register_as_super_admin(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Endpoint for super admin creation"""

    user = user_service.create_admin(db=db, schema=user)
    # create an organization for the user
    org = CreateUpdateOrganisation(
        name=f"{user.email}'s Organisation", email=user.email
    )
    organisation_service.create(db=db, schema=org, user=user)
    user_organizations = organisation_service.retrieve_user_organizations(user, db)

    # Create access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=201,
        message="User created successfully",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "is_verified", "updated_at"]
            ),
            "organisations": user_organizations,
        },
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
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def login(request: Request, login_request: LoginRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    """Endpoint to log in a user"""

    # Authenticate the user
    user = user_service.authenticate_user(
        db=db, email=login_request.email, password=login_request.password
    )
    totp_service.check_2fa_status_and_verify(db, user.id, login_request.totp_code)
    user_organizations = organisation_service.retrieve_user_organizations(user, db)

    # Generate access and refresh tokens
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    # Background task for email notification
    logger.info(f"Queueing login notification for {user.email} in the background...")
    background_tasks.add_task(send_login_notification, user, request)

    response = auth_response(
        status_code=200,
        message="Login successful",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "is_verified", "updated_at"]
            ),
            "organisations": user_organizations,
        },
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
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def logout(
    request: Request,
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
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
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
        status_code=200, message="Login successful", access_token=access_token
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
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def request_signin_token(request: Request, background_tasks: BackgroundTasks,
    email_schema: EmailRequest, db: Session = Depends(get_db)
):
    """Generate and send a 6-digit sign-in token to the user's email"""

    user = user_service.fetch_by_email(db, email_schema.email)

    token, token_expiry = user_service.generate_token()
    # Save the token and expiry
    user_service.save_login_token(db, user, token, token_expiry)

    # Send mail notification
    link = f"https://anchor-python.teams.hng.tech/login/verify-token?token={token}"

    # Send email in the background
    background_tasks.add_task(
        send_email,
        recipient=user.email,
        template_name="request-token.html",
        subject="Request Token Login",
        context={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "link": link,
        },
    )

    return success_response(
        status_code=200, message=f"Sign-in token sent to {user.email}"
    )


@auth.post("/verify-token", status_code=status.HTTP_200_OK, response_model=auth_response)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def verify_signin_token(
    request: Request, token_schema: TokenRequest, db: Session = Depends(get_db)
):
    """Verify the 6-digit sign-in token and log in the user"""

    user = user_service.verify_login_token(db, schema=token_schema)
    user_organizations = organisation_service.retrieve_user_organizations(user, db)

    # Generate JWT token
    access_token = user_service.create_access_token(user_id=user.id)
    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=200,
        message="Login successful",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "is_verified", "updated_at"]
            ),
            "organisations": user_organizations,
        },
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
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def request_magic_link(
    request: Request,
    requests: MagicLinkRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
):
    user = user_service.fetch_by_email(db=db, email=requests.email)
    magic_link_token = user_service.create_access_token(user_id=user.id)
    magic_link = f"https://anchor-python.teams.hng.tech/login/magic-link?token={magic_link_token}"

    background_tasks.add_task(
        send_magic_link,
        context={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "link": magic_link,
            "email": user.email,
        },
    )

    response = success_response(
        status_code=200, message=f"Magic link sent to {user.email}"
    )
    return response


@auth.post("/magic-link/verify")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def verify_magic_link(request: Request, token_schema: Token, db: Session = Depends(get_db)):
    user, access_token = AuthService.verify_magic_token(token_schema.token, db)
    user_organizations = organisation_service.retrieve_user_organizations(user, db)

    refresh_token = user_service.create_refresh_token(user_id=user.id)

    response = auth_response(
        status_code=200,
        message="Login successful",
        access_token=access_token,
        data={
            "user": jsonable_encoder(
                user, exclude=["password", "is_deleted", "is_verified", "updated_at"]
            ),
            "organisations": user_organizations,
        },
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


@auth.put("/password", status_code=200)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def change_password(
    request: Request,
    schema: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user: User = Depends(user_service.get_current_user),
):
    """Endpoint to change the user's password"""
    user_service.change_password(
        new_password=schema.new_password,
        user=user,
        db=db,
        old_password=schema.old_password,
    )

    return success_response(status_code=200, message="Password changed successfully")


@auth.get("/@me",
          status_code=status.HTTP_200_OK,
          response_model=AuthMeResponse)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
def get_current_user_details(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(user_service.get_current_user)],
):
    """Endpoint to get current user details."""
    profile = profile_service.fetch_by_user_id(db, current_user.id)
    organisation = organisation_service.retrieve_user_organizations(current_user, db)
    return AuthMeResponse(
        message="User details retrieved successfully",
        status_code=200,
        data={
            "user": UserData2.model_validate(current_user, from_attributes=True),
            "organisations": organisation,
            "profile": ProfileData.model_validate(profile, from_attributes=True),
        },
    )


@auth.post("/setup-2fa")
@limiter.limit("20/minute")
def setup_2fa(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(user_service.get_current_user)],
):
    """Endpoint to create a new TOTP device"""

    try:
        secret = totp_service.generate_secret()
        schema = TOTPDeviceRequestSchema(user_id=current_user.id, secret=secret)
        totp_service.create(db=db, schema=schema)
        otpauth_url = totp_service.generate_otpauth_url(
            secret=secret, user_email=current_user.email, app_name=settings.APP_NAME
        )
        qrcode_base64 = totp_service.generate_qrcode(otpauth_url)

        response_data = TOTPDeviceResponseSchema(
            secret=secret, 
            otpauth_url=otpauth_url, 
            qrcode_base64=qrcode_base64
        )
        
        return success_response(
            status_code=status.HTTP_201_CREATED,
            message="TOTP device created successfully.",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up 2FA: {str(e)}",
        )


@auth.put("/enable-2fa")
@limiter.limit("20/minute")
def enable_2fa(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    token_schema: TOTPTokenSchema,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
):
    """Endpoint to enable a TOTP device"""

    try:
        totp_device = totp_service.verify_token(
            db=db, 
            user_id=current_user.id, 
            schema=token_schema.totp_token, 
            extra_action="enable"
        )
        response_data = TOTPDeviceDataSchema(user_id=totp_device.user_id, confirmed=totp_device.confirmed)
        
        return success_response(
            status_code=status.HTTP_202_ACCEPTED,
            message="TOTP device enabled successfully.",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling totp device: {str(e)}",
        )
        

@auth.put("/disable-2fa")
@limiter.limit("20/minute")
def disable_2fa(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    token_schema: TOTPTokenSchema,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
):
    """Endpoint to disable a TOTP device"""

    try:
        totp_device = totp_service.verify_token(
            db=db, 
            user_id=current_user.id, 
            schema=token_schema.totp_token, 
            extra_action="disable"
        )
        response_data = TOTPDeviceDataSchema(user_id=totp_device.user_id, confirmed=totp_device.confirmed)
        
        return success_response(
            status_code=status.HTTP_202_ACCEPTED,
            message="TOTP device disabled successfully.",
            data=response_data.model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling totp device: {str(e)}",
        )