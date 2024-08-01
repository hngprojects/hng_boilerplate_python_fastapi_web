from pydantic import BaseModel, Field, PositiveFloat
from typing import List, Optional, Any, Dict, TypeVar, Generic, Union
from datetime import datetime

T = TypeVar('T')

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

#status filter
class ProductFilterResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    org_id: str
    category_id: str
    quantity: Optional[int] = 0
    image_url: str
    status: str
    archived: Optional[bool] = False
    filter_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SuccessResponse(BaseModel, Generic[T]):
    message: str
    status_code: int
    data: T
