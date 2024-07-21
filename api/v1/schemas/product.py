from pydantic import BaseModel
from typing import List, Optional

class ProductSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        orm_mode = True


class ProductSearchResponse(BaseModel):
    page: int
    limit: int
    total: int
    results: List[ProductSchema]
    message: str