#!/usr/bin/env python3
""" The Product model
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
)
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Product(BaseModel, Base):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
