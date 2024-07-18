#!/usr/bin/env python3
""" The Organisation model
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
from api.v1.models.base import Base, user_organisation_association


class Organisation(Base):
    __tablename__ = 'organisations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    users = relationship(
            "User",
            secondary=user_organisation_association,
            back_populates="organisations"
            )

    def __str__(self):
        return self.name
