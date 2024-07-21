#!/usr/bin/env python3
""" The Blog Post Model
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    ARRAY,
    UUID,
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Blog(BaseModel, Base):
    __tablename__ = "blogs"

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    image_url = Column(String(100), nullable=True)
    tags = Column(ARRAY(String(20)), nullable=True)

    author = relationship("User", backref="blogs")
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
