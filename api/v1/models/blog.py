from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Integer, DateTime, ARRAY
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from datetime import datetime

class Blog(BaseModel, Base):
    __tablename = "blogs"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    author_id = Column(
        String, 
        ForeignKey("users.id"), 
        nullable=False
    )
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    tags = Column(ARRAY(String(20)), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    excerpt = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)

    author = relationship("User", backref="blogs")
