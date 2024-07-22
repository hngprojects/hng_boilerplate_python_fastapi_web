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
from api.v1.models.base_model import BaseModel

# from api.v1.models.user import User

from uuid_extensions import uuid7


class Profile(BaseModel, Base):
    __tablename__ = 'profiles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(100), nullable=True)

    user = relationship("User", back_populates="profile")
