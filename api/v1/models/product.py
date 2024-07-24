
""" The Product model
"""
from sqlalchemy import (
        Column,
        String,
        Text,
        Numeric,
        ForeignKey
        )
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.orm import relationship


class Product(BaseTableModel):
    __tablename__ = 'products'

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    org_id = Column(String, ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False)

    organization = relationship("Organization", back_populates="products")
