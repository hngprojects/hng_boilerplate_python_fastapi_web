from sqlalchemy import Column, String
from api.v1.models.base_model import BaseTableModel
from api.v1.models.permissions.role_permissions import role_permissions
from sqlalchemy.orm import relationship

class Permission(BaseTableModel):
    __tablename__ = 'permissions'

    title = Column(String, unique=True, nullable=False)   

    role = relationship('Role', secondary=role_permissions, back_populates='permissions')
