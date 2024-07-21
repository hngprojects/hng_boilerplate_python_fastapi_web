#!/usr/bin/env python3
"""The Blog Post Model."""

from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from uuid_extensions import uuid7


class Blog(BaseModel, Base):
    __tablename__ = "blogs"

    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        default=uuid7
    )
    title = Column(String(100), nullable=False)
    content = Column(Text)
    image_url = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(20)), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    excerpt = Column(String(500), nullable=True)

    author = relationship("User", backref="blogs")
