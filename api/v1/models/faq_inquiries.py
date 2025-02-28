from sqlalchemy import Column, String, Text, ForeignKey
from api.v1.models.base_model import BaseTableModel
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class FAQInquiries(BaseTableModel):
    __tablename__ = "faq_inquiries"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    user = relationship("User", back_populates="faq_inquiries")