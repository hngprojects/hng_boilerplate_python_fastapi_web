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
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7


class Product(BaseTableModel):
    __tablename__ = 'products'

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
