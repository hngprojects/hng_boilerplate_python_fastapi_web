from api.v1.models.base_model import BaseTableModel
from sqlalchemy import Column, String, Integer, Float
from uuid_extensions import uuid7


class RateLimit(BaseTableModel):
    """
    Rate Limit Model
    """
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True, index=True,
                default=lambda: str(uuid7()))
    client_ip = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)
    start_time = Column(Float)
