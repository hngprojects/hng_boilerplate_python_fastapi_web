"""
Feature Request data model
"""

from sqlalchemy import Column, String, text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class FeatureRequest(BaseTableModel):
    __tablename__ = "feature_requests"

    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, server_default=text("'Low'"))  # Low, Medium, High
    status = Column(String, server_default=text("'Pending'"))  # Pending, Approved, Rejected
    is_deleted = Column(Boolean, server_default=text("false"))
    
    # Foreign Keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="feature_requests")
    
    def __str__(self):
        return self.title