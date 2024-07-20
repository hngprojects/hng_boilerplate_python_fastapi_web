#!/usr/bin/env python3
""" User data model
"""
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        Text,
        Date,
        ForeignKey,
        Numeric,
        DateTime,
        func,
        Table,
        Boolean
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, user_organization_association
from api.v1.models.base_model import BaseModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel, Base):
    """User data model.
    
    This model is used to store user data.
    eg. first_name, last_name, etc.
    no critical data should be stored here. refer to AuthUser model for that.
    """
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", uselist=False, back_populates="user")
    auth_user = relationship("AuthUser", uselist=False, back_populates="user")
    oauth_user = relationship("OAuthUser", uselist=False, back_populates="user")
    organizations = relationship(
            "Organization",
            secondary=user_organization_association,
            back_populates="users"
            )

    def to_dict(self):
        obj_dict = super().to_dict()
        return obj_dict


    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class WaitlistUser(BaseModel, Base):
    __tablename__ = 'waitlist_users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
