from pydantic import BaseModel
from datetime import datetime
from typing import List


class PaymentBase(BaseModel):
    amount: float
    currency: str
    status: str
    method: str
    created_at: datetime

class PaymentsData(BaseModel):
    current_page: int
    total_pages: int
    limit: int
    total_items: int
    Payments: List[PaymentBase]

class PaymentListResponse(BaseModel):
    status_code: int = 200
    success: bool
    message: str
    data: PaymentsData
    