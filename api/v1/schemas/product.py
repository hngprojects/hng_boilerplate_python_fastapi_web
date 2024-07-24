from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    name: str
    description: float
    price: float

class ProductData(BaseModel):
    current_page: int
    total_pages: int
    limit: int
    total_items: int
    products: List[ProductBase]

class ProductList(BaseModel):
    status_code: int = 200
    success: bool
    message: str
    data: ProductData
    