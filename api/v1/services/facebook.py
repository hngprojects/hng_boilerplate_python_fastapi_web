import requests
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from uuid_extensions import uuid7
from api.core.base.services import Service
from api.utils.settings import settings
from api.v1.routes.facebook_login import get_db
from api.v1.models import *


class FbUserService(Service):
    """Facebook User Service."""

    AdaptingMapper = {
        "username": "id",
        "password": "provider",
        "email": "email",
        "first_name": "first_name",
        "last_name": "last_name",
        "bio": "about",
    }

    def __init__(self) -> None:
        self.__clientId = getattr(settings, "FACEBOOK_APP_ID", "1675652493203580")
        self.__clientSecret = getattr(
            settings, "FACEBOOK_APP_SECRET", "4b8be6749f7d51e585daa7d4413979cf"
        )
        super().__init__()

    # ------------ CRUD functions ------------ #
    # CREATE
    def create(self, db: Annotated[Session, Depends(get_db)], fb_user_data: dict):
        """Create a new user."""
        new_user = User(
            username=fb_user_data.get(self.AdaptingMapper["username"]),
            email=fb_user_data.get(
                self.AdaptingMapper["email"], self.generateRandomEmail()
            ),
            password=fb_user_data.get(self.AdaptingMapper["password"]),
            first_name=fb_user_data.get(self.AdaptingMapper["first_name"]),
            last_name=fb_user_data.get(self.AdaptingMapper["last_name"]),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    # READ
    def fetch(self, db: Annotated[Session, Depends(get_db)], id: str):
        """Fetch a user by username."""
        user = db.query(User).filter(User.username == id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def fetch_all(self, db: Annotated[Session, Depends(get_db)]):
        """Fetch all users."""
        users = db.query(User).filter(User.password == "facebook").all()
        return users

    # UPDATE
    def update(self, db: Annotated[Session, Depends(get_db)], id: str, data: dict):
        """Update a user."""
        user = self.fetch(db, id)

        dont_update = ["id", "provider"]
        reverse_mapper = {v: k for k, v in self.AdaptingMapper.items()}
        for key, value in data.items():
            if key not in dont_update:
                setattr(user, reverse_mapper.get(key), value)
        db.commit()
        db.refresh(user)
        return user

    # DELETE
    def delete(self, db: Annotated[Session, Depends(get_db)], id: str):
        """Delete a user."""
        user = self.fetch(db, id)
        if user:
            setattr(user, "is_active", False)
            setattr(user, "is_deleted", True)
            db.commit()
        return user

    # ------------ Helper functions ------------ #
    # Validation
    def validate_facebook_token(self, user_token: str):
        """Validate Facebook token."""
        if not self.__clientId or not self.__clientSecret:
            raise HTTPException(
                400,
                "UNDEFINED ERROR: SETTING.FACEBOOK_APP_ID SETTING.FACEBOOK_APP_SECRET",
            )
        appLink = (
            "https://graph.facebook.com/oauth/access_token?client_id="
            + self.__clientId
            + "&client_secret="
            + self.__clientSecret
            + "&grant_type=client_credentials"
        )
        try:
            appToken = requests.get(appLink).json()["access_token"]
        except (ValueError, KeyError, TypeError) as error:
            return error
        secondAccessToken = (
            "https://graph.facebook.com/debug_token?input_token="
            + user_token
            + "&access_token="
            + appToken
        )
        try:
            data = requests.get(secondAccessToken).json()["data"]
            if not data.get("is_valid"):
                return None
            userId = data.get("user_id")
        except (ValueError, KeyError, TypeError) as error:
            return error
        return userId

    # Generation
    def get_facebook_user_data(self, user_token: str):
        """Retrieve Facebook user data."""
        dataLink = (
            "https://graph.facebook.com/v20.0/me?fields="
            + "id%2Cemail%2Cfirst_name%2Clast_name&about&access_token="
            + user_token
        )
        try:
            userData = requests.get(dataLink).json()
        except (ValueError, KeyError, TypeError) as error:
            return error
        userData["provider"] = "facebook"
        return userData

    def generateRandomEmail(self):
        """Generate random email."""
        return f"{uuid7()}@gmail.com"


fb_user_service = FbUserService()
