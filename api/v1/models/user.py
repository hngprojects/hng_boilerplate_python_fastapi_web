#!/usr/bin/env python3
""" User data model
"""
from sqlalchemy import (
        Column,
        String,
        text,
        Boolean
        )
from sqlalchemy.orm import relationship
from api.v1.models.base import user_organization_association, user_role_association
from api.v1.models.base_model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, server_default=text('true'))
    is_admin = Column(Boolean, server_default=text('false'))
    is_deleted = Column(Boolean, server_default=text('false'))

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary=user_organization_association, back_populates="users")
    roles = relationship('Role', secondary=user_role_association, back_populates='users')

    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict


    def __str__(self):
        return self.email

class WaitlistUser(BaseTableModel):
    __tablename__ = 'waitlist_users'

    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
