from sqlalchemy import Column, Integer, String, Float
from api.db.database import Base

class BillingPlan(Base):
    __tablename__ = "billing_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, index=True)
    amount = Column(Float)
