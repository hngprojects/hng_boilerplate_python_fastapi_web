
from fastapi import (Depends, APIRouter, Response, Request, status)
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

google_auth = APIRouter(prefix="/auth", tags=["Authentication"])
# FRONTEND_URL = config('FRONTEND_URL')

# @google_auth.get("/google")
# async def google_oauth2(request: Request) -> RedirectResponse:
#     """
#     Allows users to login using their google accounts.

#     Args:
#         request: request object

#     Returns:
#         RedirectResponse: A redirect to google authorization server for authorization
#     """
#     redirect_uri = request.url_for('google_oauth2_callback')
#     # generate a state value and stre it in the session
#     state = secrets.token_urlsafe(16)
#     request.session['state'] = state
#     response =  await google_oauth.google.authorize_redirect(request,
#                                                              redirect_uri,
#                                                              state=state)
#     return response


# @google_auth.get('/callback/google')
# async def google_oauth2_callback(request: Request,
#                                  db: Annotated[Session, Depends(get_db)]) -> Response:
#     """
#     Handles request from google after user has authenticated or
#     fails to authenticate with google account.

#     Args:
#         request: request object
#         db: database session object

#     Returns:
#         response: contains message, status code, tokens, and user data
#                     on success or HttpException if not authenticated,
#     """
#     err_message: str = 'Authentication Failed'
#     try:
#         # For testing purposes
#         if config('TESTING') != 'TEST':
#             state_in_session = request.session.get('state')
#             state_from_params = request.query_params.get('state')
#             # verify the state value to prevent CSRF
#             if state_from_params != state_in_session:
#                 return RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                         status_code=status.HTTP_302_FOUND)

#         # get the user access token and information from google authorization/resource server
#         google_response: OAuth2Token = await google_oauth.google.authorize_access_token(request)

#         # check if id_token is present
#         if 'id_token' not in google_response:
#             RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                     status_code=status.HTTP_302_FOUND)

#     except OAuthError:
#         RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                 status_code=status.HTTP_302_FOUND)

#     try:
#         if not google_response.get("access_token"):
#             RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                     status_code=status.HTTP_302_FOUND)

#         # if google has not verified the user email
#         if not google_response.get('userinfo').get('email_verified'):
#             RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                     status_code=status.HTTP_302_FOUND)

#         google_oauth_service = GoogleOauthServices()

#         tokens: object = google_oauth_service.create(google_response, db)

#         if not tokens:
#             RedirectResponse(url=f"{FRONTEND_URL}?error=true&message{err_message}",
#                                     status_code=status.HTTP_302_FOUND)

#         response = RedirectResponse(url=f"{FRONTEND_URL}/dashboard/products",
#                                     status_code=status.HTTP_302_FOUND)

#         access_token = tokens.access_token

#         refresh_token = tokens.refresh_token
        
#         response.set_cookie(key='access_token', value=access_token)

#         response.set_cookie(key='refresh_token', value=refresh_token)
#         return response
#     except Exception:
#         return RedirectResponse(url=FRONTEND_URL , status_code=status.HTTP_302_FOUND)
