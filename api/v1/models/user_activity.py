from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from api.v1.models.base import Base
from datetime import datetime
import uuid

class UserActivity(Base):
    __tablename__ = "user_activities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    activity_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)