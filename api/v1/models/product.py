#!/usr/bin/env python3
""" The Product model
"""
from sqlalchemy.sql import func
from sqlalchemy import (
        Column,
        String,
        Text,
        Numeric,
        ForeignKey,
        DateTime
        )
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.orm import relationship
from datetime import datetime


class Product(BaseTableModel):
    __tablename__ = 'products'
    pro_id = Column(Numeric, primary_key=True)    
    name = Column(String, nullable=False)
    tags = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    org_id = Column(String, ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    organization = relationship("Organization", back_populates="products")
