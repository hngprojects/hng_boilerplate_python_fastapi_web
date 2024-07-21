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
    func,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class Testimonial(BaseModel, Base):
    __tablename__ = "testimonials"

    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user = relationship("User", backref="testimonials")

    def __str__(self):
        return f"{self.firstname} {self.lastname}: {self.content}"
