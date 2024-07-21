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
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship



class Product(BaseModel, Base):
    __tablename__ = 'products'

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())



class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    slug = Column(String(100), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    children = relationship("Category")
