from pydantic import BaseModel
from typing import List, Optional


class CreateSubscriptionPlan(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    duration: str
    currency: str
    organization_id: str
    features: List[str]


class SubscriptionPlanResponse(CreateSubscriptionPlan):
    id: str

    class Config:
        from_attributes = True
