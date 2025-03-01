from pydantic import BaseModel, Field, field_validator, ConfigDict

class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=16, max_length=16, json_schema_extra={"description": "16-digit card number"})
    exp_month: int
    exp_year: int
    cvc: str = Field(..., min_length=3, max_length=4, json_schema_extra={"description": "3 or 4-digit CVC"})

    @field_validator('card_number')
    @classmethod
    def card_number_validator(cls, v):
        if not v.isdigit() or len(v) != 16:
            raise ValueError('Card number must be 16 digits')
        return v

    @field_validator('cvc')
    @classmethod
    def cvc_validator(cls, v):
        if not v.isdigit() or not (3 <= len(v) <= 4):
            raise ValueError('CVC must be 3 or 4 digits')
        return v

    model_config = ConfigDict(title="Payment Information")

class PlanUpgradeRequest(BaseModel):
    user_id: str
    plan_id: str
    is_downgrade: bool
    # payment_info: Optional[PaymentInfo] = None



