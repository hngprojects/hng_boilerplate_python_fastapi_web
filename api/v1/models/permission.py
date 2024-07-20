from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base import role_permission_association
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid7)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    roles = relationship('Role', secondary=role_permission_association, back_populates='permissions')
