from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from typing import Annotated
from api.core.responses import INVALID_CREDENTIALS, COULD_NOT_VALIDATE_CRED
from api.utils.json_response import JsonResponseDict
from api.v1.services.facebook import fb_user_service
from api.v1.services.user import user_service
from api.v1.schemas.token import OAuthToken
from api.v1.models import *

fb_auth = APIRouter(prefix="/auth", tags=["Authentication"])


@fb_auth.post("/facebook-login")
async def facebook_login(request: OAuthToken, db: Annotated[Session, Depends(get_db)]):
    is_new = False
    try:
        # get the access token from the request body
        access_token = request.access_token
        if not access_token:
            response = JsonResponseDict(
                message="Access token is required",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error=INVALID_CREDENTIALS,
            )
            return response

        # hit the Facebook Graph API to validate the access token
        try:
            fb_user_id = fb_user_service.validate_facebook_token(access_token)
        except Exception as e:
            return e
        if not fb_user_id:
            response = JsonResponseDict(
                message="Invalid access token",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error=COULD_NOT_VALIDATE_CRED,
            )
            return response
        fb_user_data = fb_user_service.get_facebook_user_data(access_token)

        # retrieve the user from the database
        try:
            user = fb_user_service.fetch(db, fb_user_id)
        except HTTPException:
            # create a new user if the user does not exist
            user, is_new = [fb_user_service.create(db, fb_user_data), True]
        # generate a jwt token based on the user id to allow for protected routes access
        token = user_service.create_access_token(str(user.id))
        code = [status.HTTP_200_OK, status.HTTP_201_CREATED]
        response = JsonResponseDict(
            message="Successfully logged in with Facebook",
            data={"access_token": f"{token}"},
            status_code=code[is_new],
        )
        return response
    except Exception as e:
        return {"status_code": 500, "message": str(e)}
