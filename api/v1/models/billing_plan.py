# app/models/billing_plan.py
from sqlalchemy import Column, String, ARRAY, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class BillingPlan(BaseTableModel):
    __tablename__ = "billing_plans"

    organization_id = Column(
        String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False, unique=True)
    price = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    description = Column(String, nullable=True)
    features = Column(ARRAY(String), nullable=False)

    organization = relationship("Organization", back_populates="billing_plans")


class UserSubscription(BaseTableModel):
    __tablename__ = "user_subscriptions"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(String, ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, default=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)

    user = relationship("User", back_populates="subscriptions")
    billing_plan = relationship("BillingPlan")