from typing import Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.product import ProductCategory
from api.v1.models.user import User

class ProductCategoryService(Service):
    """Product Category service functionality"""

    def create(self, db: Session, schema):
        """Create a new product category"""

        new_category = ProductCategory(**schema.model_dump())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)

        return new_category

    def fetch(self, db: Session, id: str) -> ProductCategory:
        """Fetches a product category by id"""

        category = check_model_existence(db, ProductCategory, id)
        return category

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all categories with option to search using query parameters"""

        query = db.query(ProductCategory)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(ProductCategory, column) and value:
                    query = query.filter(getattr(ProductCategory, column).ilike(f"%{value}%"))

        return query.all()
    
    def update(self, db: Session, id: str, schema):
        """Updates a product category"""

        category = self.fetch(db=db, id=id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, id: str, current_user: User):
        """Deletes a product category"""

        category: ProductCategory = self.fetch(db=db, id=id)

        if not current_user.is_super_admin:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        
        db.delete(category)
        db.commit()

product_category_service = ProductCategoryService()
