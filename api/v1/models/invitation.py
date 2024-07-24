from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from api.v1.models.base_model import BaseTableModel

# Invitation model
class Invitation(BaseTableModel):
    __tablename__ = 'invitations'

    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    organization_id = Column(String, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_valid = Column(Boolean, default=True)