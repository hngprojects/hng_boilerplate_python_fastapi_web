from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

from api.v1.schemas.base_schema import ResponseBase


class CreateBillingPlanSchema(BaseModel):
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


class CreateBillingPlanReturnData(CreateBillingPlanSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateBillingPlanResponse(ResponseBase):
    data: CreateBillingPlanReturnData


class GetBillingPlanData(BaseModel):
    plans: List[CreateBillingPlanReturnData]


class GetBillingPlanListResponse(ResponseBase):
    data: GetBillingPlanData