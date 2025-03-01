#!/usr/bin/env python3
"""The Session Model."""

from api.v1.models.base_model import BaseTableModel
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship


class UserSession(BaseTableModel):
    __tablename__ = "sessions"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ip_address = Column(String, nullable=False)
    location = Column(String, nullable=True)
    device = Column(String, nullable=True)
    is_revoked = Column(Boolean, server_default=text("false"))
    refresh_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")

    def __str__(self):
        return f"{self.user_id} - {self.ip_address}"