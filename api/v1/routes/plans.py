from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import Annotated
from api.v1.models.plans import SubscriptionPlan
from api.v1.schemas.plans import CreateSubscriptionPlan, SubscriptionPlanResponse
from api.db.database import get_db
from api.utils.dependencies import get_current_admin
from api.v1.models.user import User

plans = APIRouter(tags=["Plans"])

@plans.post("/plans", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_subscription_plan(plan: CreateSubscriptionPlan, db: Annotated[Session, Depends(get_db)], current_admin: Annotated[User, Depends(get_current_admin)]):
    # Check to see if the plan already exist
    db_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == plan.name).first()
    if db_plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subscription plan already exists.")
    
    # Create new plan
    db_plan = SubscriptionPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan