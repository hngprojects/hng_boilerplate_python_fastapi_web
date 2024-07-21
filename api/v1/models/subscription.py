#!/usr/bin/env python3
""" The subscription data model
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, func, Boolean, UUID
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Subscription(BaseModel, Base):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    user = relationship("User", backref="subscriptions")
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
