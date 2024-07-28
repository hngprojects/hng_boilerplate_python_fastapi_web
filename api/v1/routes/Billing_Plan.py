# routes/billing_plan.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.services.billing_plan import billing_plan_service
from api.db.database import get_db
from api.utils.json_response import JsonResponseDict
from api.v1.services.user import user_service
from api.v1.schemas.Plans import CreateBillingPlan, BillingPlanResponse

bill_plan = APIRouter(prefix='/organizations', tags=['Billing-Plan'])

@bill_plan.get('/billing-plans')
async def retrieve_all_billing_plans(
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get All Billing Plan endpoint
    """
    billing_plans = [
        {
            "id": billing_plan.id,
            "name": billing_plan.name,
            "price": float(billing_plan.price),
            "features": billing_plan.features,
        } for billing_plan in billing_plan_service.fetch_all(db=db)
    ]
    
    return JsonResponseDict(
        status_code=status.HTTP_200_OK,
        data={"plans": billing_plans},
        message="plans fetched successfully"
    )

@bill_plan.post('/billing-plans', response_model=BillingPlanResponse)
async def create_billing_plan(
    plan_data: CreateBillingPlan,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Billing Plan endpoint
    """
    billing_plan = billing_plan_service.create_billing_plan(db=db, plan_data=plan_data)
    return JsonResponseDict(
        status_code=status.HTTP_201_CREATED,
        data=billing_plan,
        message="Billing plan created successfully"
    )
