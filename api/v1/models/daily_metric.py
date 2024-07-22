from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.dialects.postgresql import UUID
from api.v1.models.base import Base
import uuid

class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, unique=True, nullable=False)
    total_users = Column(Integer, nullable=False)
    active_users = Column(Integer, nullable=False)
    new_users = Column(Integer, nullable=False)
    total_revenue = Column(Float, nullable=False)