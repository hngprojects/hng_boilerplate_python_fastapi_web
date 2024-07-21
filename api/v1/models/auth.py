#!/usr/bin/env python3
""" Auth User data model
"""
from sqlalchemy import (
    Column,
    String,
    CheckConstraint,
    ForeignKey,
    UUID,
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class AuthUser(BaseModel, Base):
    """User authentication data model.

    This model is used to store user authentication data.
    eg. password, username, email for login purposes.
    it's a one-to-one relationship with the User model.

    It has a CheckConstraint that ensures that either username or email is not null.
    so if you used username to create the user, email can be null and vice versa.
    but one of them must not be null.
    """

    __tablename__ = "auth_users"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255), nullable=False)

    user = relationship("User", uselist=False, back_populates="auth_user")

    # CheckConstraint ensures that either username or email is not null
    __table_args__ = (CheckConstraint("NOT(username IS NULL AND email IS NULL)"),)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self):
        return getattr(self, "username", self.email)


class OAuthUser(BaseModel, Base):
    """User OAuth data model.

    This model is the alternative to the AuthUser model.
    That allows users to login with their social media accounts.
    eg. Google, Facebook, Twitter, etc.
    It has a one-to-one relationship with the User model.
    """

    __tablename__ = "oauth_users"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    oauth_provider = Column(String(50), nullable=False)
    oauth_id = Column(String(60), nullable=False)
    email = Column(String(100), nullable=True)

    user = relationship("User", back_populates="oauth_user")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self):
        return getattr(self, "username", self.oauth_id)
