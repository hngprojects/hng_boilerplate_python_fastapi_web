#!/usr/bin/env python3
""" The Profile model
"""
from sqlalchemy import (
        Column,
        String,
        Text,
        ForeignKey,
        )
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseTableModel

# from api.v1.models.user import User

from uuid_extensions import uuid7


class Profile(BaseTableModel):
    __tablename__ = 'profiles'

    user_id = Column(String, ForeignKey('users.id'), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(100), nullable=True)

    user = relationship("User", back_populates="profile")
