from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from datetime import datetime, timezone


class Newsletter(BaseTableModel):
    __tablename__ = 'newsletters'

    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)

    newsletter_subscribers = relationship("NewsletterSubscriber", back_populates="newsletter")


class NewsletterSubscriber(BaseTableModel):
    __tablename__ = 'newsletter_subscribers'

    email = Column(String(120), nullable=False)
    newsletter_id = Column(Integer, ForeignKey('newsletters.id'))

    newsletter = relationship("Newsletter", back_populates="newsletter_subscribers")