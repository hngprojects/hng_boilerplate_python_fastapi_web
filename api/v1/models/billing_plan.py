# app/models/billing_plan.py
from sqlalchemy import Column, String, ARRAY, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class BillingPlan(BaseTableModel):
    __tablename__ = "billing_plans"

    organisation_id = Column(
        String, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    description = Column(String, nullable=True)
    features = Column(ARRAY(String), nullable=False)

    organisation = relationship("Organisation", back_populates="billing_plans")
