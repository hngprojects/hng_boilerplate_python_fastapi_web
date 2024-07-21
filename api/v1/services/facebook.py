import uuid
import requests

from fastapi import Depends

from sqlalchemy.orm import Session

from decouple import config
from typing import Annotated
from uuid_extensions import uuid7

from api.v1.routes.auth_facebook import get_db

# don't remove the following imports
from api.v1.models.user import User
from api.v1.models.oauth import OAuthUser
from api.v1.models.profile import Profile
from api.v1.models.org import Organization

# -------------------------------


def create_db_user(db: Annotated[Session, Depends(get_db)], fb_user_data: dict):
    new_user = User(
        username=f"watever-{uuid7()}",
        email=f"watever-{uuid7()}",
        password=f"watever",
        first_name=fb_user_data["first_name"],
        last_name=fb_user_data["last_name"],
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_oauth_user(
    db: Annotated[Session, Depends(get_db)], fb_user_id: str, user: User
):
    new_oauth_user = OAuthUser(
        oauth_provider="facebook",
        oauth_id=fb_user_id,
        user_id=user.id,
        email=getattr(user, "email", ""),
    )
    db.add(new_oauth_user)
    db.commit()
    db.refresh(new_oauth_user)
    return new_oauth_user


def validate_facebook_token(user_token: str):
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
