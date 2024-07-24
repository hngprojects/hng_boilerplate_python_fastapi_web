from pydantic import BaseModel
from decimal import Decimal

class ProductRequest(BaseModel):
    org_id: int
    pro_id: int

class ProductResponse(BaseModel):
    status: str
    message: str
    data: dict

    class Config:
        orm_mode: True
