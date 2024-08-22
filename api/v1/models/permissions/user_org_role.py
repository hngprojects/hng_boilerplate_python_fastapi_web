from sqlalchemy import Table, Column, ForeignKey, String, Boolean
from api.v1.models.base_model import BaseTableModel

user_organisation_roles = Table(
    'user_organisation_roles', BaseTableModel.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organisation_id", String, ForeignKey("organisations.id", ondelete="CASCADE"), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id', ondelete='CASCADE'), nullable=True),
    Column('is_owner', Boolean, server_default='false'),
    Column('status', String(20), nullable=False, default="active")
)