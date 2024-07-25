from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class BlogLike(BaseTableModel):
    __tablename__ = "blog_likes"

    blog_id = Column(String, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=True)

    blog = relationship("Blog", back_populates="likes")
    user = relationship("User", back_populates="blog_likes")