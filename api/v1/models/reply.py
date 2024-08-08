from sqlalchemy import String, Column, Text, ForeignKey
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.orm import relationship


class Reply(BaseTableModel):
    """
    Represents the Reply Object of a Comment.
    """
    __tablename__ = "replies"
    
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    comment_id = Column(String, ForeignKey('comments.id'), nullable=False)
    content = Column(Text, nullable=False)
    comment = relationship("Comment", back_populates="replies")
    