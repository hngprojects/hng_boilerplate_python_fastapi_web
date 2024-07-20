#!/usr/bin/env python3
""" Auth User data model
"""
from sqlalchemy import (
    Column,
    String,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
import bcrypt
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


def hash_password(password: str) -> bytes:
    """Hashes the user password for security"""
    salt = bcrypt.gensalt()

    hash_pw = bcrypt.hashpw(password.encode(), salt)
    return hash_pw


class AuthUser(Base):
    """User authentication data model.
    
    This model is used to store user authentication data.
    eg. password, username, email for login purposes.
    it's a one-to-one relationship with the User model.
    
    It has a CheckConstraint that ensures that either username or email is not null.
    so if you used username to create the user, email can be null and vice versa.
    but one of them must not be null.
    """
    __tablename__ = "auth_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255), nullable=False)

    user = relationship("User", uselist=False, back_populates="auth_user")
    
    # CheckConstraint ensures that either username or email is not null
    __table_args__ = (CheckConstraint("NOT(username IS NULL AND email IS NULL)"),)

    def __init__(self, **kwargs):
        """Initializes a user instance"""
        keys = ["username", "email", "password", "user_id"]
        for key, value in kwargs.items():
            if key in keys:
                if key == "password":
                    value = hash_password(value)
                setattr(self, key, value)

    def __str__(self):
        return getattr(self, "username", self.email)