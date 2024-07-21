#!/usr/bin/env python3
""" User data model
"""
from sqlalchemy import (
    Column,
    String,
    Boolean,
    text,
)
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseModel
from api.db.database import Base


class User(BaseModel, Base):
    __tablename__ = "users"

    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, server_default=text("false"))

    profile = relationship("Profile", uselist=False, back_populates="user")
    auth_user = relationship("AuthUser", uselist=False, back_populates="user")
    oauth_user = relationship("OAuthUser", uselist=False, back_populates="user")
    testimonials = relationship("Testimonial", back_populates="user")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class WaitlistUser(BaseModel, Base):
    __tablename__ = "waitlist_users"

    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
