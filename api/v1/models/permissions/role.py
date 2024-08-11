from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from api.v1.models.permissions.role_permissions import role_permissions

class Role(BaseTableModel):
    __tablename__ = 'roles'

    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_builtin = Column(Boolean, default=False)  # True for built-in roles, False for custom roles

    permissions = relationship('Permission', secondary=role_permissions, back_populates='role')
