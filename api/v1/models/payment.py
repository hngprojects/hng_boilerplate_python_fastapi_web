from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Payment(BaseTableModel):
    __tablename__ = "payments"

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False)  # e.g., completed, pending
    method = Column(String, nullable=False)  # e.g., credit card, PayPal
    transaction_id = Column(String, unique=True, nullable=False)

    user = relationship("User", back_populates="payments")