#!/usr/bin/python3
"""Module for bookmark model"""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Bookmark(BaseTableModel):
    __tablename__ = "bookmarks"

    user_id = Column(String, ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    user = relationship(
        "User", back_populates="bookmarks"
    )
    job = relationship(
        "Job", back_populates="bookmarks"
    )