#!/usr/bin/env python3
""" The Preference model
"""
from sqlalchemy import (
        TIMESTAMP,
        Column,
        Integer,
        String,
        Text,
        Numeric,
        DateTime,
        func,ForeignKey
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import user_organization_association
# from api.v1.models.org import Organization

from api.v1.models.base_model import BaseTableModel
from sqlalchemy.dialects.postgresql import UUID
from uuid_extensions import uuid7



# class OrgPreference(BaseModel,Base):
#      __tablename__ = 'orgpreferences'
#      id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
#      key = Column(String, index=True)
#      value = Column(String)
#      organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
#      created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
#      updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

#      organization = relationship("Organization", back_populates="orgpreferences")
class OrgPreference(BaseTableModel):
    __tablename__ = 'orgpreferences'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    key = Column(String, index=True)
    value = Column(String)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="orgpreferences")
