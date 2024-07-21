from sqlalchemy import (String, DateTime, Column, func)
from api.v1.models.base import Base
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class Oauth2_data(Base):
    """
    Model representing data from oauth2 exchange for each user
    """
    __tablename__ = 'oauth2_data'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    oauth2_provider = Column(String(60), nullable=False)
    sub = Column(String(60), nullable=False)
    access_token = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    id_token = Column(String(255), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
