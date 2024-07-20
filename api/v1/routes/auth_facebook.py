import jwt
import requests
from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.models.oauth import OAuthUser
# don't remove the following imports
from api.v1.models.profile import Profile
from api.v1.models.auth import AuthUser
from api.v1.models.org import Organization
# -------------------------------
from decouple import config
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Annotated


class userToken(BaseModel):
    access_token: str

router = APIRouter()


async def validate_facebook_token(user_token: str):
    # hit the Facebook Graph API to validate the access token
    clientId = config("FACEBOOK_APP_ID")
    clientSecret = config("FACEBOOK_APP_SECRET")
    appLink = (
        "https://graph.facebook.com/oauth/access_token?client_id="
        + clientId
        + "&client_secret="
        + clientSecret
        + "&grant_type=client_credentials"
    )
    # From appLink, retrieve the second accessToken: app access_token
    appToken = requests.get(appLink).json()["access_token"]
    link = (
        "https://graph.facebook.com/debug_token?input_token="
        + user_token
        + "&access_token="
        + appToken
    )
    try:
        data = requests.get(link).json()["data"]
        if not data.get("is_valid"):
            return None
        userId = data.get("user_id")
    except (ValueError, KeyError, TypeError) as error:
        return error
    data_link = (
        "https://graph.facebook.com/v20.0/me?fields=id%2Cemail%2Cfirst_name%2Clast_name&access_token="
        + user_token
    )
    user_data = requests.get(data_link).json()
    return [userId, user_data]


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config("SECRET_KEY"), algorithm=config("ALGORITHM")
    )
    return encoded_jwt

@router.post("/auth/facebook-login")
async def facebook_login(request: userToken, db: Session = Depends(get_db)):
    try:
        # get the access token from the request body
        access_token = request.access_token
        if not access_token:
            return {"status_code": 422, "message": "Access token is required"}

        # hit the Facebook Graph API to validate the access token
        fb_user = await validate_facebook_token(access_token)
        if not fb_user:
            return {"status_code": 400, "message": "Invalid access token"}
        fb_user_id = fb_user[0]
        fb_user_data = fb_user[1]

        # retrieve the user from the database
        user = db.query(OAuthUser).filter(OAuthUser.oauth_id == fb_user_id).first()

        if not user:
            # create a new user if the user does not exist
            new_user = User(
                first_name=fb_user_data["first_name"],
                last_name=fb_user_data["last_name"],
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            new_oauth_user = OAuthUser(
                oauth_provider="facebook",
                oauth_id=fb_user_id,
                user_id=new_user.id,
                email=getattr(new_user, "email", ""),
            )
            db.add(new_oauth_user)
            db.commit()
            db.refresh(new_oauth_user)
            user = new_user
        # generate a jwt token based on the user id to allow for protected routes access
        token = create_jwt_token({"id": str(user.id), "oauth": True})
        return {
            "status_code": 200,
            "message": "Successfully logged in with Facebook",
            "data": {"access_token": f"{token}"},
        }
    except Exception as e:
        return {"status_code": 500, "message": str(e)}
