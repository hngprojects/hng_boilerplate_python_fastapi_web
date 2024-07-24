from sqlalchemy import Column, String, Integer, ForeignKey, Table, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from api.v1.models.base import Base
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

class Invitation(BaseTableModel):
    __tablename__ = 'invitations'

    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    organization_id = Column(String, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_valid = Column(Boolean, default=True)

    user = relationship("User", back_populates="invitations")
    organization = relationship("Organization", back_populates="invitations")