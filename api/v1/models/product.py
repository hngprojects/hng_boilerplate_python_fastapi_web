#!/usr/bin/env python3
""" The Product model
"""
from sqlalchemy import (
        Column,
        String,
        Text,
        Numeric,
        )
from api.v1.models.base_model import BaseTableModel


class Product(BaseTableModel):
    __tablename__ = 'products'

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
