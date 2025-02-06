from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api.v1.models.billing_plan import BillingPlan
from typing import Any, Optional
from api.core.base.services import Service
from api.v1.schemas.plans import CreateBillingPlanSchema
from api.utils.db_validators import check_model_existence
from fastapi import HTTPException, status


class BillingPlanService(Service):
    """Product service functionality"""

    def create(self, db: Session, request: CreateBillingPlanSchema):
        """
        Create and return a new billing plan, ensuring a plan name can only exist 
        once for each 'monthly' and 'yearly' duration, and cannot be created 
        if it already exists for both durations.
        """

        # Check if a plan with the same name already exists for the provided duration
        existing_plan_for_same_duration = db.query(BillingPlan).filter(
            BillingPlan.name == request.name,
            BillingPlan.duration == request.duration
        ).first()

        if existing_plan_for_same_duration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A billing plan with the name '{request.name}' already exists for duration '{request.duration}'."
            )

        # Check if a plan with the same name exists for the other duration
        other_duration = "yearly" if request.duration == "monthly" else "monthly"
        existing_plan_for_other_duration = db.query(BillingPlan).filter(
            BillingPlan.name == request.name,
            BillingPlan.duration == other_duration
        ).first()

        if existing_plan_for_other_duration:
            # If a plan with the same name exists for both durations, raise an exception
            if existing_plan_for_same_duration and existing_plan_for_other_duration:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A billing plan with the name '{request.name}' already exists for both 'monthly' and 'yearly' durations."
                )

        # Adjust the price if the duration is 'yearly'
        if request.duration == "yearly":
            request.price = request.price * 12 * 0.8  # Apply yearly discount of 20%

        # Create a BillingPlan instance using the modified request
        plan = BillingPlan(**request.dict())

        try:
            db.add(plan)
            db.commit()
            db.refresh(plan)
            return plan
        
        except IntegrityError as e:
            db.rollback()
            # Check if it's a foreign key violation error
            if "foreign key constraint" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organisation with id {request.organisation_id} not found."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A database integrity error occurred."
                )

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred."
            )



    def delete(self, db: Session, id: str):
        """
        delete a plan by plan id
        """
        plan = check_model_existence(db, BillingPlan, id)

        db.delete(plan)
        db.commit()

    def fetch(self, db: Session, billing_plan_id: str):
        billing_plan = db.query(BillingPlan).get(billing_plan_id)

        if billing_plan is None:
            raise HTTPException(
                status_code=404, detail="Billing plan not found."
            )

        return billing_plan

    def update(self, db: Session, id: str, schema):
        """
        fetch and update a billing plan
        """
        plan = check_model_existence(db, BillingPlan, id)

        update_data = schema.dict(exclude_unset=True)
        for column, value in update_data.items():
            setattr(plan, column, value)

        db.commit()
        db.refresh(plan)

        return plan

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all products with option tto search using query parameters"""

        query = db.query(BillingPlan)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(BillingPlan, column) and value:
                    query = query.filter(
                        getattr(BillingPlan, column).ilike(f"%{value}%")
                    )

        return query.all()


billing_plan_service = BillingPlanService()
