from fastapi import (
    APIRouter,
    Depends,
    status,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.billing_plan import billing_plan_service
from api.db.database import get_db
from api.v1.services.user import user_service
from api.v1.schemas.plans import CreateSubscriptionPlan

bill_plan = APIRouter(prefix="/organizations", tags=["Billing-Plan"])


@bill_plan.get("/billing-plans", response_model=success_response)
async def retrieve_all_billing_plans(db: Session = Depends(get_db)):
    """
    Endpoint to get all billing plans
    """

    plans = billing_plan_service.fetch_all(db=db)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plans fetched successfully",
        data={
            "plans": jsonable_encoder(plans),
        },
    )


@bill_plan.post("/billing-plans", response_model=success_response)
async def create_new_billing_plan(
    request: CreateSubscriptionPlan,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Endpoint to create new billing plan
    """

    plan = billing_plan_service.create(db=db, request=request)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plans created successfully",
        data=jsonable_encoder(plan),
    )
