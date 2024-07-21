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

    @classmethod
    def from_orm(cls, orm_category):
        return cls(
            id=orm_category.id,
            name=orm_category.name,
            description=orm_category.description,
            slug=orm_category.slug,
            parent_id=orm_category.parent_id
        )

class CategoryList(BaseModel):
    status_code: int = 200
    categories: List[Category]