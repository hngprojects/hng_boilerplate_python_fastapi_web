from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID
from datetime import datetime




class PaymentsResponse(BaseModel):
    user_id: str
    amount: float
    currency: str
    status: str 
    method: str 
    transaction_id: str


    class Config:
        from_attributes = True


