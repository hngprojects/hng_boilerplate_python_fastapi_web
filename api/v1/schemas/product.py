from pydantic import BaseModel

class ProductUpdate(BaseModel):
    product_name: str
    price: float
    description: str
    tag: str

    class Config:
        orm_mode = True