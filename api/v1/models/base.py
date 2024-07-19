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
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()

user_organization_association = Table('user_organization', Base.metadata,
        Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
        Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id'), primary_key=True)
        )
