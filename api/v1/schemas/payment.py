from pydantic import BaseModel
from typing import Optional

class PaymentSchema(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    method: str
    transaction_id: str

# class CreatePaymentSchema(BaseModel):
#     amount: float
#     currency: str
#     status: str
#     method: str
#     transaction_id: str
#     user_id: Optional[str] = None