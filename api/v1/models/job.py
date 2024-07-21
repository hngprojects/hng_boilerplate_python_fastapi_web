#!/usr/bin/env python3
""" The Job Model Class
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Date,
        ForeignKey,
        Numeric,
        DateTime,
        func,
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID


class Job(BaseModel, Base):
    __tablename__ = 'jobs'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, default=uuid7)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255))
    salary = Column(Numeric(10, 2))
    job_type = Column(String(50))
    company_name = Column(String(255))
    
    # Define relationship with User
    user = relationship("User", backref="jobs")
