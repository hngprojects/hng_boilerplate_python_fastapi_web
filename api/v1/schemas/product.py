from pydantic import BaseModel
from typing import List

class ProductBase(BaseModel):
    name: str
    description: str
    price: float

class ProductList(BaseModel):
    status_code: int
    data: List[ProductBase]