#!/usr/bin/env python3
""" OAuth User data model
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class OAuthUser(Base):
    """User OAuth data model.
    
    This model is the alternative to the AuthUser model.
    That allows users to login with their social media accounts.
    eg. Google, Facebook, Twitter, etc.
    It has a one-to-one relationship with the User model.
    """
    __tablename__ = "oauth_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    oauth_provider = Column(String(50), nullable=False)
    oauth_id = Column(String(60), nullable=False)
    email = Column(String(100), nullable=True)

    user = relationship("User", back_populates="oauth_user")

    def __init__(self, **kwargs):
        """Initializes a user instance"""
        keys = ["oauth_provider", "oauth_id", "user_id"]
        for key, value in kwargs.items():
            if key in keys:
                setattr(self, key, value)

    def __str__(self):
        return getattr(self, "username", self.oauth_id)