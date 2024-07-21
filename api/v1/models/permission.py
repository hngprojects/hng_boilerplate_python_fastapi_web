from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from api.v1.models.base import role_permission_association
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

class Permission(BaseModel, Base):
    __tablename__ = 'permissions'

    name = Column(String, unique=True, index=True, nullable=False)

    roles = relationship('Role', secondary=role_permission_association, back_populates='permissions')
