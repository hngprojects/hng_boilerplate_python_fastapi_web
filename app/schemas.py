# api/schemas.py
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

    class Config:
        orm_mode = True

class ProductResponse(BaseModel):
    status: str
    message: str
    status_code: int
    data: Product
