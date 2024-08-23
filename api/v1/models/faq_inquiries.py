from sqlalchemy import Column, String, Text
from api.v1.models.base_model import BaseTableModel


class FAQInquiries(BaseTableModel):
    __tablename__ = "faq_inquiries"

    email = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
