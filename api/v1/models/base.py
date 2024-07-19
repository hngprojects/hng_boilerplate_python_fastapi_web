#!/usr/bin/env python3
""" Base
"""
from sqlalchemy import (
        Column,
        Integer,
        ForeignKey,
        Table
        )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()

user_organization_association = Table('user_organization', Base.metadata,
        Column('user_id', UUID(as_uuid=True), ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
        Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True)
        )

user_role_association = Table('user_role', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id',  ondelete='CASCADE'), primary_key=True)
)

role_permission_association = Table(
    'role_permission', Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id',  ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id',  ondelete='CASCADE'), primary_key=True)
)



