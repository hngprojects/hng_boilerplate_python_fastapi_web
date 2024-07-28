#!/usr/bin/env python3
""" The Job Model Class
"""
from sqlalchemy import (
        Column,
        String,
        Text,
        ForeignKey
        )
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Job(BaseTableModel):
    __tablename__ = 'jobs'
    
    author_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    salary = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

    author = relationship("User", back_populates="jobs")