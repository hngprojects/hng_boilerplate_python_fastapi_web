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
from api.v1.schemas.plans import (
    CreateBillingPlanSchema, CreateBillingPlanResponse, GetBillingPlanListResponse
)


bill_plan = APIRouter(prefix="/organisations", tags=["Billing-Plan"])


@bill_plan.get("/{organisation_id}/billing-plans", response_model=GetBillingPlanListResponse)
async def retrieve_all_billing_plans(
    organisation_id: str, db: Session = Depends(get_db)
):
    """
    Endpoint to get all billing plans
    """

    plans = billing_plan_service.fetch_all(db=db, organisation_id=organisation_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plans fetched successfully",
        data={
            "plans": jsonable_encoder(plans),
        },
    )


@bill_plan.post("/billing-plans", response_model=CreateBillingPlanResponse)
async def create_new_billing_plan(
    request: CreateBillingPlanSchema,
    _: User = Depends(user_service.get_current_super_admin),
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


@bill_plan.patch("/billing-plans/{billing_plan_id}", response_model=CreateBillingPlanResponse)
async def update_a_billing_plan(
    billing_plan_id: str,
    request: CreateBillingPlanSchema,
    _: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Endpoint to update a billing plan by ID
    """

    plan = billing_plan_service.update(db=db, id=billing_plan_id, schema=request)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plan updated successfully",
        data=jsonable_encoder(plan),
    )


@bill_plan.delete("/billing-plans/{billing_plan_id}", response_model=success_response)
async def delete_a_billing_plan(
    billing_plan_id: str,
    _: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Endpoint to delete a billing plan by ID
    """

    billing_plan_service.delete(db=db, id=billing_plan_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plan deleted successfully",
    )


@bill_plan.get('/billing-plans/{billing_plan_id}', response_model=CreateBillingPlanResponse)
async def retrieve_single_billing_plans(
    billing_plan_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(user_service.get_current_user)
):
    """
    Endpoint to get single billing plan by id
    """

    billing_plan = billing_plan_service.fetch(db, billing_plan_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Plan fetched successfully",
        data=jsonable_encoder(billing_plan)
    )