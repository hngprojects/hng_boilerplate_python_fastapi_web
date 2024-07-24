""" User data model
"""
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        Text,
        text,
        Date,
        ForeignKey,
        Numeric,
        DateTime,
        func,
        Table,
        Boolean
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, user_organization_association, user_newsletter_association
from api.v1.models.base_model import BaseTableModel



class User(BaseTableModel):
    __tablename__ = 'users'

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary=user_organization_association, back_populates="users")
    roles = relationship('Role', secondary=user_role_association, back_populates='users')

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict


    def __str__(self):
        return self.email