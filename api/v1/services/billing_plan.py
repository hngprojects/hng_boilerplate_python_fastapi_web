from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api.v1.models.billing_plan import BillingPlan
from typing import Any, Optional
from api.core.base.services import Service
from api.v1.schemas.plans import CreateSubscriptionPlan
from api.utils.db_validators import check_model_existence
from fastapi import HTTPException, status


class BillingPlanService(Service):
    """Product service functionality"""

    def create(self, db: Session, request: CreateSubscriptionPlan):
        """
        Create and return a new billing plan
        """
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
