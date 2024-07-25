from sqlalchemy import Column, String, Text
from uuid import uuid4
from sqlalchemy.orm import relationship
from datetime import datetime
from api.db.database import Base
from api.v1.models.base import user_newsletter_association
from api.v1.models.base_model import BaseTableModel


class Newsletter(BaseTableModel):
    """
    Newsletter db model
    """
    __tablename__ = 'newsletters'

    email = Column(String(150), unique=True, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)

    subscribers = relationship("User", secondary=user_newsletter_association, back_populates="newsletters")