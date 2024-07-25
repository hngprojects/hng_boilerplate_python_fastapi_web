from sqlalchemy.orm import Session
from api.v1.models.billing_plan import BillingPlan

class PlanService:
    def get_billing_plan_details(self, db: Session, organization_id: str, plan_name: str):
        '''Function to fetch Billing Plan details for an organization'''
        billing_plan = db.query(BillingPlan).filter(
            BillingPlan.organization_id == organization_id,
            BillingPlan.name == plan_name
        ).first()

        return billing_plan

plan_service = PlanService()
