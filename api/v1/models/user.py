#!/usr/bin/env python3
""" User data model
"""
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        Text,
        text,
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
from api.v1.models.base import Base, user_organization_association, user_role_association
from api.v1.models.profile import Profile
from api.v1.models.org import Organization
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel, Base):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, server_default=text('true'))
    is_admin = Column(Boolean, server_default=text('false'))
    is_admin = Column(Boolean, default=False) # required for certain operation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary=user_organization_association, back_populates="users")
    roles = relationship('Role', secondary=user_role_association, back_populates='users')
    profile = relationship("Profile", uselist=False, back_populates="user")
    organizations = relationship(
            "Organization",
            secondary=user_organization_association,
            back_populates="users"
            )
    
   



    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict


    def __str__(self):
        return self.email

class WaitlistUser(BaseModel, Base):
    __tablename__ = 'waitlist_users'

    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
