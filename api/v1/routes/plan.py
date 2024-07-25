from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.plan import SubscriptionPlanResponse
from api.v1.services.plan import plan_service
from api.v1.services.user import user_service
from api.utils.success_response import success_response

plan_router = APIRouter(prefix='/plans', tags=['Plans'])

@plan_router.get('/organizations/{organization_id}/billing-plans/{plan_name}', status_code=status.HTTP_200_OK, response_model=SubscriptionPlanResponse)
async def get_billing_plan_details(
    organization_id: str,
    plan_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    '''Endpoint to get Billing Plan details'''
    billing_plan = plan_service.get_billing_plan_details(db, organization_id, plan_name)

    if billing_plan is None:
        raise HTTPException(status_code=404, detail="Billing plan not found")

    return success_response(
        status_code=200,
        message='details fetched successfully',
        data={'plan': billing_plan}
    )
