from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    currency: str
    status: str
    method: str
    transaction_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
