#!/usr/bin/env python3
""" Associations
"""
from sqlalchemy import (
        Column,
        ForeignKey,
        String,
        Table,
    )
from sqlalchemy.dialects.postgresql import UUID
from api.db.database import Base


user_organization_association = Table('user_organization', Base.metadata,
	Column('user_id', String, ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
	Column('organization_id', String, ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True)
)