#!/usr/bin/env python3
"""
Testimonial data model
map testimonial table into 
a python object (Testimonial class)
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.user import User
from uuid_extensions import uuid7
from sqlalchemy.dialects.postgresql import UUID

class Testimonial(Base):
    __tablename__ = 'testimonials'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    user = relationship("User", backref("testimonials", cascade="all, delete-orphan"))

    def __init__(self, firstname, lastname, content, user_id):
        self.firstname = firstname
        self.lastname = lastname
        self.content = content
        self.user_id = user_id

    def __str__(self):
        return f"{self.firstname} {self.lastname}: {self.content}"

