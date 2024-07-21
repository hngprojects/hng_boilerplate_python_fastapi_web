from sqlalchemy import Column, String, Integer, ForeignKey, Table, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from api.v1.models.base import role_permission_association, user_role_association
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

class Role(BaseModel, Base):
    __tablename__ = 'roles'

    role_name = Column(String, unique=True, index=True, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id',  ondelete='CASCADE'), nullable=False)
    is_active = Column(Boolean, default=True)

    permissions = relationship('Permission', secondary=role_permission_association, back_populates='roles')
    organization = relationship('Organization', back_populates='roles')
    users = relationship('User', secondary=user_role_association, back_populates='roles')