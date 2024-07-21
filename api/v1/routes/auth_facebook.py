import uuid

from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session
from api.db.database import get_db

from decouple import config
from datetime import timedelta
from typing import Annotated

from api.core.responses import INVALID_CREDENTIALS, COULD_NOT_VALIDATE_CRED

from api.utils.auth import create_access_token
from api.utils.json_response import JsonResponseDict

from api.v1.services.facebook import validate_facebook_token, create_db_user, create_oauth_user

from api.v1.schemas.facebook import userToken

from api.v1.models import *

fb_auth = APIRouter(prefix="/auth", tags=["auth"])

@fb_auth.post("/facebook-login")
async def facebook_login(request: userToken, db: Annotated[Session, Depends(get_db)]):
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
        fb_user = validate_facebook_token(access_token)
        if not fb_user:
            response = JsonResponseDict(
                message="Invalid access token",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error=COULD_NOT_VALIDATE_CRED,
            )
            return response
        fb_user_id = fb_user[0]
        fb_user_data = fb_user[1]

        # retrieve the user from the database
        oauth_user = db.query(OAuthUser).filter(OAuthUser.oauth_id == fb_user_id).first()

        if not oauth_user:
            # create a new user if the user does not exist
            user, is_new = [create_db_user(db, fb_user_data), True]
            create_oauth_user(db, fb_user_id, user)
        else:
            user = db.get(User, oauth_user.user_id)
            if not user:
                user = create_db_user(db, fb_user_data)
        # generate a jwt token based on the user id to allow for protected routes access
        token = create_access_token(
            {"username": str(user.username), "oauth": True},
            timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))),
        )
        code = [status.HTTP_200_OK, status.HTTP_201_CREATED]
        response = JsonResponseDict(
            message="Successfully logged in with Facebook",
            data={"access_token": f"{token}"},
            status_code=code[is_new],
        )
        return response
    except Exception as e:
        return {"status_code": 500, "message": str(e)}
