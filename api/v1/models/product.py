#!/usr/bin/env python3
""" The Product model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Numeric,
        DateTime,
        func,
        )
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7


class Product(BaseModel, Base):
    __tablename__ = 'products'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
