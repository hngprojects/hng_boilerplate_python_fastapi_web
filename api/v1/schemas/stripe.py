from typing import List, Optional

from pydantic import BaseModel, Field, validator


class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=16, max_length=16)
    exp_month: int
    exp_year: int
    cvc: str = Field(..., min_length=3, max_length=4)

    @validator('card_number')
    def card_number_validator(cls, v):
        if not v.isdigit() or len(v) != 16:
            raise ValueError('Card number must be 16 digits')
        return v

    @validator('cvc')
    def cvc_validator(cls, v):
        if not v.isdigit() or not (3 <= len(v) <= 4):
            raise ValueError('CVC must be 3 or 4 digits')
        return v


class PlanUpgradeRequest(BaseModel):
    user_id: str
    plan_id: str
    is_downgrade: bool
    #payment_info: Optional[PaymentInfo] = None


