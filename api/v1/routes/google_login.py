from fastapi import (Depends, status, APIRouter,
                     Response, Request, HTTPException)
from sqlalchemy.orm import Session
from typing import Annotated
from starlette.responses import RedirectResponse
from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
import secrets

from api.db.database import get_db
from api.core.dependencies.google_oauth_config import google_oauth
from api.v1.services.google_oauth import GoogleOauthServices

google_auth = APIRouter(prefix="/auth", tags=["Authentication"])


@google_auth.get("/google-login")
async def google_oauth2(request: Request) -> RedirectResponse:
    """
    Allows users to login using their google accounts.

    Args:
        request: request object

    Returns:
        RedirectResponse: A redirect to google authorization server for authorization
    """
    redirect_uri = request.url_for('google_oauth2_callback')
    # generate a state value and stre it in the session
    state = secrets.token_urlsafe(16)
    request.session['state'] = state
    response =  await google_oauth.google.authorize_redirect(request,
                                                             redirect_uri,
                                                             state=state)
    return response


@google_auth.get('/callback/google')
async def google_oauth2_callback(request: Request,
                                 db: Annotated[Session, Depends(get_db)]) -> Response:
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
    try:
        state_in_session = request.session.get('state')
        state_from_params = request.query_params.get('state')
        # verify the state value tomprevent CSRF
        if state_from_params != state_in_session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="CSRF Warning! State not equal in request and response.")
        # get the user access token and information from google authorization/resource server
        google_response: OAuth2Token = await google_oauth.google.authorize_access_token(request)

        # check if id_token is present
        if 'id_token' not in google_response:
            raise HTTPException(status_code=400, detail="Authentication Failed")

    except OAuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")

    try:
        if not google_response.get("access_token"):
            raise HTTPException(status_code=400, detail="Authentication Failed")

        # if google has not verified the user email
        if not google_response.get('userinfo').get('email_verified'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Authentication Failed")
        google_oauth_serivce = GoogleOauthServices()
        return google_oauth_serivce.create(google_response, db)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Authentication Failed")