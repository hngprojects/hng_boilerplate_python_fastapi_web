from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    slug: str
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        orm_mode = True

class CategoryList(BaseModel):
    status_code: int = 200
    categories: List[Category]