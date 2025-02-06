# app/models/billing_plan.py
from sqlalchemy import Column, String, ARRAY, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
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
    user_subscriptions = relationship("UserSubscription", back_populates="billing_plan", cascade="all, delete-orphan")


class UserSubscription(BaseTableModel):
    __tablename__ = "user_subscriptions"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(String, ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False)
    organisation_id = Column(String, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, default=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=True)
    
    user = relationship("User", back_populates="subscriptions")
    billing_plan = relationship("BillingPlan", back_populates="user_subscriptions")
    organisation = relationship("Organisation", back_populates="user_subscriptions")
    billing_cycle = Column(DateTime, nullable=True)
