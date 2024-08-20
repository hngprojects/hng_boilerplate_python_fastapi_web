
""" The Organisation model
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.models.base_model import BaseTableModel


class Organisation(BaseTableModel):
    __tablename__ = "organisations"

    name = Column(String, nullable=False, unique=False)
    email = Column(String, nullable=True, unique=True)
    industry = Column(String, nullable=True)
    type = Column(String, nullable=True)
    description = Column(String, nullable=True)
    country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    address = Column(String, nullable=True)

    users = relationship(
        "User", secondary=user_organisation_roles, back_populates="organisations"
    )
    billing_plans = relationship("BillingPlan", back_populates="organisation", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organisation", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organisation", cascade="all, delete-orphan")
    contact_us = relationship("ContactUs", back_populates="organisation", cascade="all, delete-orphan")
    
    user_subscriptions = relationship("UserSubscription", back_populates="organisation", cascade="all, delete-orphan")
    sales = relationship('Sales', back_populates='organisation', cascade='all, delete-orphan')

    def __str__(self):
        return self.name
