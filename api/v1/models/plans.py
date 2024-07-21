#!/usr/bin/env python3
""" The plan data model
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
        Boolean,
        ARRAY
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class SubscriptionPlan(BaseModel, Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    duration = Column(String(50), nullable=False)
    features = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
