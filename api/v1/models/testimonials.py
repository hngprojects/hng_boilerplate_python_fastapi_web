    #!/usr/bin/env python3
""" The Product model
"""
from sqlalchemy import (
        Column,
        Integer,
        String,
        Text,
        Numeric,
        DateTime,
        func,
        )
from datetime import datetime
from api.v1.models.base import Base
from api.v1.models.base_model import BaseModel
from sqlalchemy.dialects.postgresql import UUID


class Testimonial(BaseModel, Base):
    __tablename__ = 'testimonies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_name = Column(String, nullable=False)
    client_designation = Column(String, nullable=False)
    testimonial = Column(Text, nullable=True)
    rating = Column(Numeric, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
 