from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class Waitlist(BaseTableModel):
    __tablename__ = "waitlist"

    email = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())