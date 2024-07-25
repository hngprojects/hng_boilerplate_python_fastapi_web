#!/usr/bin/env python3
"""The Blog Post Model."""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
# from api.v1.models.base import Base
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from uuid_extensions import uuid7


class Blog(BaseTableModel):
    __tablename__ = "blogs"

    author_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"))
    excerpt = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Assuming tags are stored as a comma-separated string

    author = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete-orphan")
    likes = relationship("BlogLike", back_populates="blog", cascade="all, delete-orphan")
    dislikes = relationship("BlogDislike", back_populates="blog", cascade="all, delete-orphan")