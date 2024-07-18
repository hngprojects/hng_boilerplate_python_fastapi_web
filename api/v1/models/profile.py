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
from datetime import datetime
from api.v1.models.base import Base


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #user = relationship("User", back_populates="profile")
