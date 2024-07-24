#!/usr/bin/env python3
""" The subscription data model
"""
from sqlalchemy import (
        Column,
        String,
        ForeignKey,
        DateTime,
        func,
        Boolean
        )
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Subscription(BaseTableModel):
    __tablename__ = 'subscriptions'

    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    plan = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    user = relationship("User", backref="subscriptions")
