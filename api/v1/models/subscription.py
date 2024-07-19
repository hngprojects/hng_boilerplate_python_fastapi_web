#!/usr/bin/env python3
""" The subscription data model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Date,
        ForeignKey,
        DateTime,
        func,
        Boolean
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, BaseModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class Subscription(BaseModel, Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    plan = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    user = relationship("User", backref="subscriptions")
