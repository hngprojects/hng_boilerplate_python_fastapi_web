from fastapi import BackgroundTasks, Depends, APIRouter, status, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
from starlette.responses import RedirectResponse
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
import secrets
from decouple import config

from api.db.database import get_db
from api.core.dependencies.google_oauth_config import google_oauth
from api.v1.services.google_oauth import GoogleOauthServices
from api.utils.success_response import success_response
from api.v1.schemas.google_oauth import OAuthToken
from api.v1.services.user import user_service
from fastapi.encoders import jsonable_encoder
import requests
from datetime import timedelta

google_auth = APIRouter(prefix="/auth", tags=["Authentication"])
FRONTEND_URL = config("FRONTEND_URL")


@google_auth.post("/google", status_code=200)
async def google_login(background_tasks: BackgroundTasks, token_request: OAuthToken, db: Session = Depends(get_db)):
    """
    Handles Google OAuth login.

    Args:
    - background_tasks (BackgroundTasks): Background tasks to be executed.
    - token_request (OAuthToken): OAuth token request.
    - db (Session): Database session.

    Returns:
    - JSONResponse: JSON response with user details and access token.

    Example:
    ```
    POST /google HTTP/1.1
    Content-Type: application/json

    {
        "id_token": "your_id_token_here"
    }
    ```
    """
    try:

        id_token = token_request.id_token
        profile_endpoint = f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}'
        profile_response = requests.get(profile_endpoint)
        
        if profile_response.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token or failed to fetch user info")
        
        profile_data = profile_response.json()

        
        email = profile_data.get('email')
        user = user_service.get_user_by_email(db=db, email=email)

        # Check if the user exists
        if user:
            # User already exists, return their details
            access_token = user_service.create_access_token(user_id=user.id)
            refresh_token = user_service.create_refresh_token(user_id=user.id)
            response = JSONResponse(
                status_code=200,
                content={
                    "status_code": 200,
                    "message": "Login successful",
                    "access_token": access_token,
                    "data": {
                        "user": jsonable_encoder(
                            user, exclude=["password", "is_deleted", "updated_at"]
                        )
                    },
                },
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                expires=timedelta(days=30),
                httponly=True,
                secure=True,
                samesite="none",
            )
            return response
        else:

            google_oauth_service = GoogleOauthServices()
            # User does not exist, create a new user
            user = google_oauth_service.create(background_tasks=background_tasks, db=db, google_response=profile_data)
            access_token = user_service.create_access_token(user_id=user.id)
            refresh_token = user_service.create_refresh_token(user_id=user.id)
            response = JSONResponse(
                status_code=200,
                content={
                    "status_code": 200,
                    "message": "Login successful",
                    "access_token": access_token,
                    "data": {
                        "user": jsonable_encoder(
                            user, exclude=["password", "is_deleted", "updated_at"]
                        )
                    },
                },
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                expires=timedelta(days=30),
                httponly=True,
                secure=True,
                samesite="none",
            )
            return response
    except ValueError:
        # Invalid ID token
        return JSONResponse(status_code=401, content={"error": "Invalid ID token"})
    


@google_auth.get("/callback/google")
async def google_oauth2_callback(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> Response:
    """
    Handles request from google after user has authenticated or
    fails to authenticate with google account.

    Args:
        request: request object
        db: database session object

    Returns:
        response: contains message, status code, tokens, and user data
                    on success or HttpException if not authenticated,
    """
    
    err_message: str = 'Authentication Failed'
    try:
        # For testing purposes
        if config("TESTING") != "TEST":
            state_in_session = request.session.get("state")
            state_from_params = request.query_params.get("state")
            # verify the state value to prevent CSRF
            if state_from_params != state_in_session:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}?error=true&message{err_message}",
                    status_code=status.HTTP_302_FOUND,
                )

        # get the user access token and information from google authorization/resource server
        google_response: OAuth2Token = await google_oauth.google.authorize_access_token(
            request
        )

        # check if id_token is present
        if "id_token" not in google_response:
            RedirectResponse(
                url=f"{FRONTEND_URL}?error=true&message{err_message}",
                status_code=status.HTTP_302_FOUND,
            )

    except OAuthError:
        RedirectResponse(
            url=f"{FRONTEND_URL}?error=true&message{err_message}",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        if not google_response.get("access_token"):
            RedirectResponse(
                url=f"{FRONTEND_URL}?error=true&message{err_message}",
                status_code=status.HTTP_302_FOUND,
            )

        # if google has not verified the user email
        if not google_response.get("userinfo").get("email_verified"):
            RedirectResponse(
                url=f"{FRONTEND_URL}?error=true&message{err_message}",
                status_code=status.HTTP_302_FOUND,
            )

        google_oauth_service = GoogleOauthServices()

        tokens: object = google_oauth_service.create(google_response, db)

        if not tokens:
            RedirectResponse(
                url=f"{FRONTEND_URL}?error=true&message{err_message}",
                status_code=status.HTTP_302_FOUND,
            )

        response = RedirectResponse(
            url=f"{FRONTEND_URL}/dashboard/products", status_code=status.HTTP_302_FOUND
        )

        access_token = tokens.access_token

        refresh_token = tokens.refresh_token

        response.set_cookie(key="access_token", value=access_token)

        response.set_cookie(key="refresh_token", value=refresh_token)
        return response
    except Exception:
        return RedirectResponse(url=FRONTEND_URL, status_code=status.HTTP_302_FOUND)
