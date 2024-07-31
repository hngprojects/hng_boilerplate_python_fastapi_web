from decimal import Decimal
from pydantic import BaseModel, Field, PositiveFloat, constr
from typing import List, Optional, Any, Dict
from datetime import datetime

from api.v1.models.product import ProductStatusEnum


class ProductUpdate(BaseModel):
    """
    Pydantic model for updating a product.

    This model is used for validating and serializing data when updating
    a product in the system. It ensures that the `name` field is a required
    string, the `price` is a positive float, and the `updated_at` field
    is a datetime object that indicates when the product was last updated.

    Attributes:
        name (str): The name of the product. This field is required.
        price (PositiveFloat): The price of the product. Must be a positive number.
        description (Optional[str]): An optional description of the product.
        updated_at (datetime): The date and time when the product was last updated.
    """

    name: str = Field(..., alias="name", description="Name of the product")
    price: PositiveFloat
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ResponseModel(BaseModel):
    """
    A model to structure the response for the Product Update endpoint

    Attributes:
        success (bool): Indicates if the request was successful.
        status_code (int): HTTP status code of the response.
        message (str): A message describing the result.
        data (Optional[Dict[str, Any]]): Optional data payload of the respons
    """

    success: bool
    status_code: int
    message: str
    data: Optional[Dict[str, Any]] = None


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


class ProductCreate(BaseModel):
    name: str = Field(..., description="Name of the product")
    description: Optional[str] = Field(None, description="Description of the product")
    price: Decimal = Field(..., description="Price of the product")
    org_id: str = Field(..., description="Organization ID that the product belongs to")
    category_id: str = Field(..., description="Category ID that the product belongs to")
    quantity: Optional[int] = Field(0, description="Quantity of the product in stock")
    image_url: str = Field(..., description="URL of the product image")
    status: Optional[ProductStatusEnum] = Field(ProductStatusEnum.in_stock, description="Current status of the product")

    class Config:
        orm_mode = True