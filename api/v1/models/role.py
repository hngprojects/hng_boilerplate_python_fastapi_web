from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from api.v1.models.base import role_permission_association, user_role_association

class Role(BaseTableModel):
    __tablename__ = 'roles'

    role_name = Column(String, index=True, nullable=False)
    organization_id = Column(String, ForeignKey('organizations.id',  ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)

    permissions = relationship('Permission', secondary=role_permission_association, back_populates='roles')
    organization = relationship('Organization', back_populates='roles')
    users = relationship('User', secondary=user_role_association, back_populates='roles')