# app/models/contact_us.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class ContactUs(BaseTableModel):
    __tablename__ = "contact_us"

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    org_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    organization = relationship("Organization", back_populates="contact_us")
