from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class Notification(BaseTableModel):
    __tablename__ = "notifications"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default='unread')  # unread, read

    user = relationship("User", back_populates="notifications")