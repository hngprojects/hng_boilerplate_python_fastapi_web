#!/usr/bin/env python3
"""The Blog Post Model."""

<<<<<<< HEAD
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

=======
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from uuid_extensions import uuid7
from api.utils.settings import settings
>>>>>>> upstream/backend

class Blog(BaseTableModel):
    __tablename__ = "blogs"
    prod_env = settings.dev in ["dev", "prod"]
    author_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
<<<<<<< HEAD
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    is_deleted = Column(Boolean, server_default=text("false"))
    excerpt = Column(Text, nullable=True)
    tags = Column(
        Text, nullable=True
    )  # Assuming tags are stored as a comma-separated string
=======
    title = Column(String(100), nullable=False)
    content = Column(Text)
    image_url = Column(String(100), nullable=True)
    if prod_env:
        tags = Column(ARRAY(String(20)), nullable=True)
    else:
        tags = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    excerpt = Column(String(500), nullable=True)
>>>>>>> upstream/backend

    author = relationship("User", back_populates="blogs")
    comments = relationship(
        "Comment", back_populates="blog", cascade="all, delete-orphan"
    )
    likes = relationship(
        "BlogLike", back_populates="blog", cascade="all, delete-orphan"
    )
    dislikes = relationship(
        "BlogDislike", back_populates="blog", cascade="all, delete-orphan"
    )


class BlogDislike(BaseTableModel):
    __tablename__ = "blog_dislikes"

    blog_id = Column(String, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)

    # Relationships
    blog = relationship("Blog", back_populates="dislikes")
    user = relationship("User", back_populates="blog_dislikes")


class BlogLike(BaseTableModel):
    __tablename__ = "blog_likes"

    blog_id = Column(String, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)

    blog = relationship("Blog", back_populates="likes")
    user = relationship("User", back_populates="blog_likes")
