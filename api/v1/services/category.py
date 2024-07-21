from sqlalchemy.orm import Session
from ..models.product import Category
from typing import Optional

def get_categories(db: Session, skip: int = 0, limit: int = 100, parent_id: Optional[int] = None):
    query = db.query(Category)
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    return query.offset(skip).limit(limit).all()