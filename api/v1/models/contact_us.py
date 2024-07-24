# app/models/contact_us.py
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class ContactUs(BaseTableModel):
    __tablename__ = "contact_us"

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
