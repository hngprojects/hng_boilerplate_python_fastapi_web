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


class Organization(BaseTableModel):
    __tablename__ = 'organizations'

    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)

    users = relationship(
            "User",
            secondary=user_organization_association,
            back_populates="organizations"
            )
    roles = relationship('Role', back_populates='organization')


    def __str__(self):
        return self.name
