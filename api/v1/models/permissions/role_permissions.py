from sqlalchemy import Table, Column, ForeignKey, String
from api.v1.models.base_model import BaseTableModel

role_permissions = Table(
    'role_permissions', BaseTableModel.metadata,
    Column('role_id', String, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', String, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)
