#!/usr/bin/env python3
""" The Organization model
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Table,
    UUID,
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel

user_organization_association = Table(
    "user_organization",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        primary_key=True,
    ),
)


class Organization(BaseModel, Base):
    __tablename__ = "organizations"

    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship(
        "User", secondary=user_organization_association, backref="organizations"
    )
    roles = relationship("Role", back_populates="organization")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name
