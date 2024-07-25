from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.v1.models.billing_plan import BillingPlan
from api.v1.models.user import User
from api.v1.services.user import UserService


class PlanService:
    def get_billing_plan(self, db: Session, organization_id: str, plan_name: str, user: User):
        """Fetch a specific billing plan"""
        
        # Check if the user is authorized to view the plan
        if not user.is_super_admin:
            raise HTTPException(status_code=403, detail="You do not have permission to access this resource")

        # Fetch the billing plan
        billing_plan = db.query(BillingPlan).filter(BillingPlan.organization_id == organization_id, BillingPlan.name == plan_name).first()

        if not billing_plan:
            raise HTTPException(status_code=404, detail="Billing plan not found")

        return billing_plan

plan_service = PlanService()
