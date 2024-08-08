from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCommentBase(BaseModel):
    content: str = Field(..., example="This is a comment")
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

    class Config:
        orm_mode = True


class ProductCommentResponse(BaseModel):
    status_code: int
    success: bool
    message: str
    data: ProductCommentInDB