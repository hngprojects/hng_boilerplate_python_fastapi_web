#!/usr/bin/env python3
""" ActivityLog data model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        DateTime,
        ForeignKey,
        func
        )
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class ActivityLog(BaseModel, Base):
    __tablename__ = 'activity_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key column
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="activity_logs")

    def __str__(self):
        return f"ActivityLog({self.user_id}, {self.action}, {self.timestamp})"