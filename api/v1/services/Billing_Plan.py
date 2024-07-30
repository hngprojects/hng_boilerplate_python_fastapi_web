# services/billing_plan.py
from sqlalchemy.orm import Session
from api.v1.models.Billing_Plan import BillingPlan
from api.v1.schemas.Plans import CreateBillingPlan

class BillingPlanService:
    def create_billing_plan(self, db: Session, plan_data: CreateBillingPlan) -> BillingPlan:
        billing_plan = BillingPlan(**plan_data.dict())
        db.add(billing_plan)
        db.commit()
        db.refresh(billing_plan)
        return billing_plan
        
    def fetch_all(self, db: Session):
        return db.query(BillingPlan).all()

    def get_billing_plan_by_id(self, db: Session, plan_id: str) -> BillingPlan:
        return db.query(BillingPlan).filter(BillingPlan.id == plan_id).first()



billing_plan_service = BillingPlanService()
