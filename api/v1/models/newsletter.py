from sqlalchemy import Column, String, DateTime
from uuid import uuid4
from datetime import datetime
from api.v1.models.base import Base 


class NEWSLETTER(Base):
    """
    Newsletter db model
    """
    __tablename__ = 'newsletters'

    id = Column(String(500), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 