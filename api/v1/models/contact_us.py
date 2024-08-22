from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class ContactUs(BaseTableModel):
    __tablename__ = "contact_us"

    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    org_id = Column(String, ForeignKey('organisations.id', ondelete="CASCADE"), nullable=True)

    organisation = relationship("Organisation", back_populates="contact_us")