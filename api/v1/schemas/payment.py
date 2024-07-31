from pydantic import BaseModel
from typing import List
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
        from_attributes = True

        
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
