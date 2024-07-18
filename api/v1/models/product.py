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


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
