""" Associations
"""
from sqlalchemy import (
        Column,
        ForeignKey,
        String,
        Table,
        DateTime,
        func
    )
from api.db.database import Base


user_organization_association = Table('user_organization', Base.metadata,
	Column('user_id', String, ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
	Column('organization_id', String, ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True),
    Column('status', String(20), nullable=False, default="member")
)

user_newsletter_association = Table(
    'user_newsletter_association',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('newsletter_id', String, ForeignKey('newsletters.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

user_password_reset_otp_association = Table(
    'user_password_reset_otp_association',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id', primary_key=True)),
    Column('otp_id', String, ForeignKey('otp.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)