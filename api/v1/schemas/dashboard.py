from typing import List
from datetime import datetime
from pydantic import BaseModel


class ProductPaginationBase(BaseModel):
    limit: int
    offset: int
    pages: int
    total_items: int


class DashboardProductBase(BaseModel):
    id: str
    name: str
    description: str
    price: str
    quantity: int
    image_url: str
    archived: bool
    category_name: str
    organization_name: str
    created_at: datetime
    category_id: str
    organization_id: str


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
    pagination: ProductPaginationBase
    data: List[DashboardProductBase]
