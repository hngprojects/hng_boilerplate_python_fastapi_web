from sqlalchemy import Table, Column, ForeignKey, String
from api.v1.models.base_model import BaseTableModel

user_organization_roles = Table(
    'user_organization_roles', BaseTableModel.metadata,
    Column("user_id", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("organization_id", String, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column('role_id', String, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False),
    Column('status', String(20), nullable=False, default="active")
)