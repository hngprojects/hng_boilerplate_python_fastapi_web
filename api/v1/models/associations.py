""" Associations
"""
from sqlalchemy import (
        Column,
        ForeignKey,
        String,
        Table,
        Enum
    )
from api.db.database import Base


user_organization_association = Table('user_organization', Base.metadata,
	Column('user_id', String, ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
	Column('organization_id', String, ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True),
    Column('role', Enum('admin', 'user', 'guest', 'owner', name='user_org_role'), nullable=False, default="user"),
    Column('status', Enum('member', 'suspended', 'left', name='user_org_status'), nullable=False, default="member")
)
