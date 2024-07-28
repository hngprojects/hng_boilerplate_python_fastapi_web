# schemas/plans.py
from pydantic import BaseModel
from typing import List, Optional
import uuid

class CreateBillingPlan(BaseModel):
    name: str
    price: float
    currency: str
    features: List[str]
    organization_id: str

class BillingPlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    currency: str
    features: List[str]
    organization_id: str

    class Config:
        orm_mode=True
