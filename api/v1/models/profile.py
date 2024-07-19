#!/usr/bin/env python3
""" The Profile model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Date,
        ForeignKey,
        DateTime,
        func,
        )
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from api.v1.models.base import Base
from uuid_extensions import uuid7


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id',  ondelete='CASCADE'), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")
