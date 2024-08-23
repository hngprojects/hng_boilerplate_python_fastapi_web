from pydantic import BaseModel
from typing import List, Optional


class CreateSubscriptionPlan(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    duration: str
    currency: str
    organisation_id: str
    features: List[str]


class SubscriptionPlanResponse(CreateSubscriptionPlan):
    id: str

    class Config:
        from_attributes = True


class BillingPlanSchema(BaseModel):
    id: str
    organisation_id: str
    name: str
    price: float
    currency: str
    duration: str
    description: Optional[str] = None
    features: List[str]

    class Config:
        orm_mode = True