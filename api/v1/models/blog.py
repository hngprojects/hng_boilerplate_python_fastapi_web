#!/usr/bin/env python3
""" The Blog Post Model
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
        Boolean
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, BaseModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID, ARRAY


class Blog(BaseModel, Base):
    __tablename__ = 'blogs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    image_url = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(20)), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    author = relationship("User", backref="blogs")
