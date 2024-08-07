#!/usr/bin/env python3
""" The Job Model Class
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Job(BaseTableModel):
    __tablename__ = "jobs"

    author_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)
    salary = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

    author = relationship("User", back_populates="jobs")
    applications = relationship('JobApplication', back_populates='job')


class JobApplication(BaseTableModel):
    __tablename__ = "job_applications"

    job_id = Column(
        String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    applicant_name = Column(String, nullable=False)
    applicant_email = Column(String, nullable=False)
    cover_letter = Column(Text, nullable=True)
    resume_link = Column(String, nullable=False)
    portfolio_link = Column(String, nullable=True)
    application_status = Column(Enum('pending', 'accepted', 'rejected', name='application_status'), default="pending")

    job = relationship('Job', back_populates='applications')
