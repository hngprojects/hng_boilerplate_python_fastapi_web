# app/models/message.py
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class Message(BaseTableModel):
    __tablename__ = "messages"

    message = Column(Text, nullable=False)
    phone_number = Column(String, nullable=True)
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="messages")
