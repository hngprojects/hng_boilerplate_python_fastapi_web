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
from datetime import datetime
from api.v1.models.base import Base, user_organization_association
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7


class Organization(BaseTableModel):
    __tablename__ = 'organizations'

    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    users = relationship(
            "User",
            secondary=user_organization_association,
            back_populates="organizations"
            )
    roles = relationship('Role', back_populates='organization')

    orgpreferences = relationship("OrgPreference", back_populates="organization") #required

    def __str__(self):
        return self.name
