from fastapi import (
    APIRouter,
    Depends,
    status
    )
from sqlalchemy.orm import Session
from api.v1.schemas.plans import BillingPlanDisplay
from api.v1.models.user import User
from api.v1.services.plan import billing_plan_service
from api.db.database import get_db
from api.utils.json_response import JsonResponseDict
from api.utils.dependencies import get_current_user

plan = APIRouter(prefix='/api/v1/organizations', tags=['Billing-Plan'])

@plan.post('/12345/billing-plans', response_model=JsonResponseDict)
async def retrieve_all_billing_plans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get All Billing Plan endpoint
    """
    billing_plans: list[BillingPlanDisplay] = billing_plan_service()
    
    return JsonResponseDict(
        status_code=status.HTTP_200_OK,
        data={
            "plans": billing_plans
            },
        message="plans fetched successfully"
        
    )

