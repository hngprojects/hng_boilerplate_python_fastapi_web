from typing import Any, Optional
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status


from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.product import (
    Product,
    ProductFilterStatusEnum,
    ProductStatusEnum,
    ProductCategory,
)
from api.v1.models.user import User
from api.v1.models import Organisation
from api.v1.schemas.product import ProductCategoryCreate, ProductCreate
from api.utils.db_validators import check_user_in_org
from api.v1.schemas.product import ProductFilterResponse


class ProductService(Service):
    """Product service functionality"""

    # def check_ownership(
    #     self, db: Session, current_user: User, product: Product, org_id: str
    # ):
    #     # check ownership

    #     if org_id != product.org_id:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="product doesn't belong to the specified organisation",
    #         )

    #     organisation = check_model_existence(db, Organisation, org_id)

    #     check_user_in_org(user=current_user, organisation=organisation)

    def create(
        self, db: Session, schema: ProductCreate, org_id: str, current_user: User
    ):
        """Create a new product"""

        # check if user belongs to org

        organisation = check_model_existence(db, Organisation, org_id)

        check_user_in_org(user=current_user, organisation=organisation)

        # check if user inputted a valid category

        category_name = schema.category
        category = (
            db.query(ProductCategory)
            .filter(func.lower(ProductCategory.name) == func.lower(category_name))
            .first()
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{category_name} category does not exist",
            )

        # add org_id, category_id and remove category field from schema

        product_schema = schema.model_dump()
        product_schema.pop("category")
        product_schema["category_id"] = category.id
        product_schema["org_id"] = org_id

        # create new product

        new_product = Product(**product_schema)

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product

    def fetch_single_by_organisation(
        self, db: Session, org_id: str, product_id: str, current_user: User
    ) -> Product:
        """Fetches a product by id"""

        # check if user belongs to org

        organisation = check_model_existence(db, Organisation, org_id)

        check_user_in_org(user=current_user, organisation=organisation)

        product = check_model_existence(db, Product, product_id)
        return product

    def update(
        self, db: Session, product_id: str, current_user: User, org_id: str, schema
    ):
        """Updates a product"""

        product = self.fetch_single_by_organisation(
            db, org_id, product_id, current_user
        )

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, org_id: str, product_id: str, current_user: User):
        """Deletes a product"""

        product: Product = self.fetch_single_by_organisation(
            db, org_id, product_id, current_user
        )

        # delete the product

        db.delete(product)
        db.commit()

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all products with option tto search using query parameters"""

        query = db.query(Product)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Product, column) and value:
                    query = query.filter(
                        getattr(Product, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str) -> Product:
        """Fetches a product by id"""

        product = check_model_existence(db, Product, id)
        return product

    def fetch_by_organisation(self, db: Session, user, org_id, limit, page):
        """Fetches all products of an organisation"""

        # check if organisation exists
        organisation = check_model_existence(db, Organisation, org_id)

        # Check if the user exist in the organisation
        check_user_in_org(user=user, organisation=organisation)

        # calculating offset value from page and limit given
        offset_value = (page - 1) * limit

        # Filter to return only products of the org_id
        products = (
            db.query(Product)
            .filter(Product.org_id == org_id)
            .offset(offset_value)
            .limit(limit)
            .all()
        )

        return products

    def fetch_by_filter_status(
        self, db: Session, org_id: str, filter_status: ProductFilterStatusEnum
    ):
        """Fetch products by filter status"""
        try:
            products = (
                db.query(Product)
                .filter(Product.org_id == org_id)
                .filter(Product.filter_status == filter_status.value)
                .all()
            )
            return [ProductFilterResponse.from_orm(product) for product in products]
        except Exception as e:
            raise

    def fetch_by_status(self, db: Session, org_id: str, status: ProductStatusEnum):
        """Fetch products by filter status"""
        try:
            products = (
                db.query(Product)
                .filter(Product.org_id == org_id)
                .filter(Product.status == status.value)
                .all()
            )
            response_data = [
                ProductFilterResponse.from_orm(product) for product in products
            ]
            return response_data
        except Exception as e:
            raise

    def fetch_stock(
        self, db: Session, product_id: str, current_user: User, org_id: str
    ) -> dict:
        """Fetches the current stock level for a specific product"""
        product = self.fetch_single_by_organisation(
            db=db, org_id=org_id, product_id=product_id, current_user=current_user
        )

        total_stock = product.quantity

        return {
            "product_id": product_id,
            "current_stock": total_stock,
            "last_updated": product.updated_at,
        }

    def search_products(
            db: Session,
            org_id: str,
            name: Optional[str] = None,
            category: Optional[str] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            limit: int = 10,
            page: int = 1,
    ):

        query = db.query(Product).filter(Product.org_id == org_id)

        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))

        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()

        return products


class ProductCategoryService(Service):
    """Product categories service functionality"""

    @staticmethod
    def create(db: Session, schema: ProductCategoryCreate, current_user: User):
        # organisation = check_model_existence(db, Organisation, org_id)

        # check_user_in_org(user=current_user, organisation=organisation)

        try:
            new_category = ProductCategory(**schema.model_dump())
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists.",
            )

        return new_category

    @staticmethod
    def fetch_all(db: Session, **query_params: Optional[Any]):
        """Fetch all newsletter subscriptions with option to search using query parameters"""

        query = db.query(ProductCategory)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(ProductCategory, column) and value:
                    query = query.filter(
                        getattr(ProductCategory, column).ilike(f"%{value}%")
                    )

        return query.all()


product_service = ProductService()
