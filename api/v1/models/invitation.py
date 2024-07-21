from sqlalchemy import Column, String, Integer, ForeignKey, Table, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from api.v1.models.base import role_permission_association, user_role_association
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

# Invitation model
class Invitation(BaseModel, Base):
    __tablename__ = 'invitations'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_valid = Column(Boolean, default=True)