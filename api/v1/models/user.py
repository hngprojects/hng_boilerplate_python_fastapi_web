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
        Table
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, user_organization_association, BaseModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel, Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
