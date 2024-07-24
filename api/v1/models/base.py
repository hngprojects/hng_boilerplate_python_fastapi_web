""" Associations
"""
from sqlalchemy import (
        Column,
        ForeignKey,
        String,
        Table,
        Integer,
        DateTime,
        func
    )
from sqlalchemy.dialects.postgresql import UUID
from api.db.database import Base


user_organization_association = Table('user_organization', Base.metadata,
	Column('user_id', String, ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
	Column('organization_id', String, ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True)
)

user_newsletter_association = Table(
    'user_newsletter_association',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('newsletter_id', String, ForeignKey('newsletters.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)