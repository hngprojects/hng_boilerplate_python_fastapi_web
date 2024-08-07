
""" The Organization model
"""
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship
from api.v1.models.associations import user_organization_association
from api.v1.models.base_model import BaseTableModel


class Organization(BaseTableModel):
    __tablename__ = "organizations"

    name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=True, unique=True)
    industry = Column(String, nullable=True)
    type = Column(String, nullable=True)
    description = Column(String, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    address = Column(String, nullable=True)

    users = relationship(
        "User", secondary=user_organization_association, back_populates="organizations"
    )
    billing_plans = relationship("BillingPlan", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    contact_us = relationship("ContactUs", back_populates="organization", cascade="all, delete-orphan")
    
    billing_plans = relationship(
        "BillingPlan", back_populates="organization", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation", back_populates="organization", cascade="all, delete-orphan"
    )
    products = relationship(
        "Product", back_populates="organization", cascade="all, delete-orphan"
    )
    sales = relationship('Sales', back_populates='organization',
                         cascade='all, delete-orphan')

    def __str__(self):
        return self.name
