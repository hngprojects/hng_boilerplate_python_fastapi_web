#!/usr/bin/env python3
"""
Testimonial data model
map testimonial table into 
a python object (Testimonial class)
"""
from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    UUID
)
from sqlalchemy.orm import relationship
from api.db.database import Base
from api.v1.models.base_model import BaseModel

class Testimonial(BaseModel, Base):
    __tablename__ = 'testimonials'

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="testimonials")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname}: {self.content}"