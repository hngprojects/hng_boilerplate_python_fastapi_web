from sqlalchemy import String, Column, Text, ForeignKey
from api.v1.models.base_model import BaseTableModel


class Reply(BaseTableModel):
    """
    Represents the Reply Object of a Comment.
    """
    __tablename__ = "replies"
    
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    comment_id = Column(String)
    content = Column(Text, nullable=False)
    