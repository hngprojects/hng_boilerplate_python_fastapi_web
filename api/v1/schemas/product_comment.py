from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ProductCommentBase(BaseModel):
    content: str = Field(..., json_schema_extra={"example": "This is a comment"})
    author: str


class ProductCommentCreate(ProductCommentBase):
    pass

class ProductCommentUpdate(ProductCommentBase):
    pass


class ProductCommentInDB(ProductCommentBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCommentResponse(BaseModel):
    status_code: int
    success: bool
    message: str
    data: ProductCommentInDB