from pydantic import BaseModel
from typing import Optional, Literal

class PaymentSchema(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    method: str
    transaction_id: str

class CreatePaymentSchema(BaseModel):
    amount: float
    currency: str
    status: Literal["completed", "pending"]
    method: str
    user_id: Optional[str] = None