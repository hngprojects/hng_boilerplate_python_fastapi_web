from sqlalchemy.orm import Session
from api.v1.models import billing_plan
from typing import Optional

def create_billing_plan(db: Session, plan_name: str, amount: float) -> billing_plan:
    """Crée un plan de facturation dans la base de données."""
    if not plan_name:
        raise ValueError("Plan name is required")
    if amount <= 0:
        raise ValueError("Amount must be a positive number")
    
    new_plan = BillingPlan(plan_name=plan_name, amount=amount)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

