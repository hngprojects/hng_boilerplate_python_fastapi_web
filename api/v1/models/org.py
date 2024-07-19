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
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7

class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship(
            "User",
            secondary=user_organization_association,
            back_populates="organizations"
            )
    roles = relationship('Role', back_populates='organization')
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")

    def __str__(self):
        return self.name
