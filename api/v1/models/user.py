#!/usr/bin/env python3
""" User data model
"""
from sqlalchemy import (create_engine, Column, Integer, String, Text,
                        Date, ForeignKey, Numeric, DateTime, func, Table, Boolean )

from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, user_organization_association, user_role_association
import bcrypt
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary=user_organization_association, back_populates="users")
    roles = relationship('Role', secondary=user_role_association, back_populates='users')
    
    def __init__(self, **kwargs):
        """ Initializes a user instance
        """
        keys = ['username', 'email', 'password', 'first_name', 'last_name']
        for key, value in kwargs.items():
            if key in keys:
                if key == 'password':
                    value = hash_password(value)
                setattr(self, key, value)

    def __str__(self):
        return self.email

