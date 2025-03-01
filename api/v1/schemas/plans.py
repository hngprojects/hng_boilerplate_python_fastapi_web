from pydantic import BaseModel, Field, field_validator, ConfigDict
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

    @field_validator("price")
    @classmethod
    def adjust_price(cls, value, values):
        duration = values.data.get("duration")
        if duration == "yearly":
            value = int(value * 12 * 0.8)  # Multiply by 12 and apply a 20% discount
        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        v = value.lower()
        if v not in ["monthly", "yearly"]:
            raise ValueError("Duration must be either 'monthly' or 'yearly'")
        return v

    model_config = ConfigDict(title="Create Billing Plan")


class CreateBillingPlanReturnData(CreateBillingPlanSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateBillingPlanResponse(ResponseBase):
    data: CreateBillingPlanReturnData


class GetBillingPlanData(BaseModel):
    plans: List[CreateBillingPlanReturnData]


class GetBillingPlanListResponse(ResponseBase):
    data: GetBillingPlanData
