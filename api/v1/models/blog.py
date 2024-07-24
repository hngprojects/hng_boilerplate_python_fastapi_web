from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, ARRAY
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from datetime import datetime


class Blog(BaseTableModel):
    __tablename__ = "blogs"

    # id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author_id = Column(String, ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    image_url = Column(ARRAY(String), nullable=True)
    is_deleted = Column(Boolean, default=False)
    excerpt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    tags = Column(ARRAY(String), nullable=True)
    likes = Column(Integer, nullable=True)
    dislikes = Column(Integer, nullable=True)

    likes_audit = Column(ARRAY(String), nullable=True)

    dislikes_audit = Column(ARRAY(String), nullable=True)

    author = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete-orphan")
    likes = relationship("BlogLike", back_populates="blog", cascade="all, delete-orphan")
    dislikes = relationship("BlogDislike", back_populates="blog", cascade="all, delete-orphan")
