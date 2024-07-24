# app/models/billing_plan.py
from sqlalchemy import Column, String, ARRAY, ForeignKey, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class BillingPlan(BaseTableModel):
    __tablename__ = "billing_plans"

    organization_id = Column(String, ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    features = Column(ARRAY(String), nullable=False)

    organization = relationship("Organization", back_populates="billing_plans")
