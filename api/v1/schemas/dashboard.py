from typing import List
from datetime import datetime
from pydantic import BaseModel



class DashboardProductBase(BaseModel):
    name: str
    description: str
    price: str
    category: str
    quantity: int
    image_url: str
    archived: bool
    created_at: datetime


class DashboardResponseBase(BaseModel):
    status_code: int = 200
    success: bool
    message: str


class ProductCountBase(BaseModel):
    count: int


class DashboardProductCountResponse(DashboardResponseBase):
    data: ProductCountBase


class DashboardSingleProductResponse(DashboardResponseBase):
    data: DashboardProductBase


class DashboardProductListResponse(DashboardResponseBase):
    data: List[DashboardProductBase]
