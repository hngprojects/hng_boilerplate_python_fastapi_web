from pydantic import BaseModel, EmailStr, Field, PositiveFloat, ConfigDict, StringConstraints
from typing import List, Optional, Any, Dict, TypeVar, Generic, Annotated, List
from datetime import datetime


T = TypeVar("T")


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


class ProductStockResponse(BaseModel):
    product_id: str
    current_stock: int
    last_updated: datetime


class ProductList(BaseModel):
    status_code: int = 200
    success: bool
    message: str
    data: ProductData


class ProductCategoryBase(BaseModel):
    id: str
    name: str


class ProductVariantBase(BaseModel):
    id: str
    size: str
    price: float
    stock: int


class ProductDetailOrganisation(BaseModel):
    id: str
    company_name: str
    company_email: EmailStr | None = None
    industry: str | None = None
    organisation_type: str | None = None
    country: str | None = None
    state: str | None = None
    address: str | None = None
    lga: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductDetail(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    organisation: ProductDetailOrganisation
    quantity: int
    image_url: str
    status: str
    archived: bool
    variants: list[ProductVariantBase]
    category: ProductCategoryBase

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: ProductDetail


# status filter
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


class ProductCreate(BaseModel):
    name: str
    category: str
    price: PositiveFloat
    description: str = None
    quantity: int = 0
    image_url: str = "placeholder-image"

class ProductCategoryRetrieve(BaseModel):
    name: str
    id: str
    class Config:
        from_attributes = True

class ProductCategoryCreate(BaseModel):
    name: str

class ProductCategoryData(BaseModel):
    name: str


class ProductCommentCreate(BaseModel):
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]



class ProductCommentsSchema(BaseModel):
    """
    Schema for Product Comments
    """

    user_id: str = ""
    product_id: str = ""
    content: str = ""
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)
