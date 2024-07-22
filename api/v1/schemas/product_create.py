from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        orm_mode = True


class ProductResponse(BaseModel):
    name: str
    description: str
    price: float
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SuccessResponse(BaseModel):
    status: str
    message: str
    data: ProductResponse


class ErrorResponse(BaseModel):
    status_code: int
    status: str
    message: str
    errors: ProductResponse
