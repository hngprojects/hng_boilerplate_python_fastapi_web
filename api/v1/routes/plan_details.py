from fastapi import Depends, HTTPException, APIRouter, Request, Response, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.plan import plan_service
from api.v1.models.user import User
from api.v1.schemas.plan import SubscriptionPlanResponse
from api.core.dependencies.auth import get_current_user

plan_router = APIRouter(prefix='/plans', tags=['Plans'])

@plan_router.get('/{organization_id}/billing-plans/{plan_name}', response_model=SubscriptionPlanResponse)
def get_billing_plan_details(
    organization_id: str,
    plan_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Endpoint to get Billing Plan Details"""
    plan = plan_service.get_billing_plan_details(db, organization_id, plan_name)
    if not plan:
        raise HTTPException(status_code=404, detail="Billing plan not found")
    return plan
