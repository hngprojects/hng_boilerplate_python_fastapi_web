#!/usr/bin/env python3
"""The Blog Post Model."""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from uuid_extensions import uuid7
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


class Blog(BaseTableModel, Base):
    __tablename__ = "blogs"
    
    author_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
    )
    title = Column(String(100), nullable=False)
    content = Column(Text)
    image_url = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(20)), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    excerpt = Column(String(500), nullable=True)
    
    author = relationship("User", backref="blogs")