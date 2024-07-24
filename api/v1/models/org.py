#!/usr/bin/env python3
""" The Organization model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Date,
        ForeignKey,
        Numeric,
        DateTime,
        func,
        )
from sqlalchemy.orm import relationship
from api.v1.models.base import user_organization_association
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7


class Organization(BaseTableModel):
    __tablename__ = 'organizations'

    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    users = relationship(
            "User",
            secondary=user_organization_association,
            back_populates="organizations"
            )
    roles = relationship("OrgRole", back_populates="organization", cascade="all, delete-orphan")
    billing_plans = relationship("BillingPlan", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    
    def __str__(self):
        return self.name
