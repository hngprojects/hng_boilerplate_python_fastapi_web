from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from api.v1.models.base import Base
from uuid_extensions import uuid7

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
