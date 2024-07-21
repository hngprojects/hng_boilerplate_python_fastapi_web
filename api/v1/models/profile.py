#!/usr/bin/env python3
""" The Profile model
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    UUID,
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Profile(BaseModel, Base):
    __tablename__ = "profiles"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    bio = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(100), nullable=True)

    user = relationship("User", back_populates="profile")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)