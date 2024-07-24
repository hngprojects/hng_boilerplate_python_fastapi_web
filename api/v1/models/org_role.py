from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel
from uuid_extensions import uuid7

class OrgRole(BaseTableModel):
    __tablename__ = "org_roles"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    org_id = Column(String, ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False)
    is_admin = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="roles")
    user = relationship("User", back_populates="roles")