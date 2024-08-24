from sqlalchemy import Column, DateTime, String, Text, Numeric, func
from api.v1.models.base_model import BaseTableModel

class APIStatus(BaseTableModel):
    __tablename__ = "api_status"

    api_group = Column(String, nullable=False)
    status = Column(String, nullable=False)
    last_checked = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    response_time = Column(Numeric, nullable=True)
    details = Column(Text, nullable=True)
