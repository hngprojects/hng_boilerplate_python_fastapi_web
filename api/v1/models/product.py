""" The Product model
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    ForeignKey,
    Integer,
    Enum as SQLAlchemyEnum,
    Boolean,
    DateTime,
    func,
)
from api.v1.models.base_model import BaseTableModel
from api.v1.models import User
from sqlalchemy.orm import relationship
from enum import Enum


class ProductStatusEnum(Enum):
    in_stock = "in_stock"
    out_of_stock = "out_of_stock"
    low_on_stock = "low_on_stock"

class ProductFilterStatusEnum(Enum):
    active = "active"
    draft = "draft"

class Product(BaseTableModel):
    __tablename__ = "products"

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric, nullable=False)
    org_id = Column(
        String, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False
    )
    category_id = Column(
        String, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, default=0)
    image_url = Column(String, nullable=False)
    status = Column(
        SQLAlchemyEnum(ProductStatusEnum), default=ProductStatusEnum.in_stock
    )
    archived = Column(Boolean, default=False)
    filter_status = Column(
        SQLAlchemyEnum(ProductFilterStatusEnum), default=ProductFilterStatusEnum.active
    )

    variants = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )
    organisation = relationship("Organisation", back_populates="products")
    category = relationship("ProductCategory", back_populates="products")
    sales = relationship('Sales', back_populates='product',
                         cascade='all, delete-orphan')
    comments = relationship("ProductComment", back_populates="product", cascade="all, delete-orphan")


    def __str__(self):
        return self.name


class ProductVariant(BaseTableModel):
    __tablename__ = "product_variants"

    size = Column(String, nullable=False)
    stock = Column(Integer, default=1)
    price = Column(Numeric)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    product = relationship("Product", back_populates="variants")


class ProductCategory(BaseTableModel):
    __tablename__ = "product_categories"

    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="category")

    def __str__(self):
        return self.name


class ProductComment(BaseTableModel):
    __tablename__ = "product_comments"

    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True) 
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="comments")
    user = relationship("User", back_populates="product_comments")  

    def __str__(self):
        return f"Comment by User ID: {self.user_id} on Product ID: {self.product_id}"