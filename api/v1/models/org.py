#!/usr/bin/env python3
"""
The Organization model
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
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7


class Organization(Base):
    """
    Class defination for organization model
    """
    __tablename__ = 'organizations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    slug = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
        )
    email = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
        )
    owner = relationship(
        "User",
        back_populates="user_orgs"
    )

    users = relationship(
            "User",
            secondary=user_organization_association,
            back_populates="organizations"
            )
    roles = relationship('Role', back_populates='organization')


    def __str__(self):
        return self.name
