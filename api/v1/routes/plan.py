from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.plans import SubscriptionPlanResponse
from api.v1.services.user import user_service
from api.v1.services.plan import plan_service

plan = APIRouter(prefix='/plans', tags=['Plans'])

@plan.get('{organization_id}/billing-plans/{plan_name}', response_model=SubscriptionPlanResponse, status_code=status.HTTP_200_OK)
def get_billing_plan(organization_id: str, plan_name: str, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    """Endpoint to get Billing Plan Details"""
    
    billing_plan = plan_service.get_billing_plan(db=db, organization_id=organization_id, plan_name=plan_name, user=current_user)
    
    return billing_plan
