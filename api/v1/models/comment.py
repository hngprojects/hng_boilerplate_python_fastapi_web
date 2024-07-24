from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Comment(BaseTableModel):
    __tablename__ = "comments"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    blog_id = Column(String, ForeignKey('blogs.id', ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="comments")
    blog = relationship("Blog", back_populates="comments")