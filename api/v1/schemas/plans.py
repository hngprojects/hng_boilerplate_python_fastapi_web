from pydantic import BaseModel, validator
from typing import List, Optional


class CreateSubscriptionPlan(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    duration: str
    currency: str
    organisation_id: str
    features: List[str]

    @validator("price")
    def adjust_price(cls, value, values):
        duration = values.get("duration")
        if duration == "yearly":
            value = value * 12 * 0.8  # Multiply by 12 and apply a 20% discount
        return value

    @validator("duration")
    def validate_duration(cls, value):
        v = value.lower()
        if v not in ["monthly", "yearly"]:
            raise ValueError("Duration must be either 'monthly' or 'yearly'")
        return v


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