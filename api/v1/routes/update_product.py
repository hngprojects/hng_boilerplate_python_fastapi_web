#!/usr/bin/env python3
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from pydantic import BaseModel, validator
from fastapi.security import OAuth2PasswordBearer
from api.v1.models.product import Product as ProductModel
from api.v1.schemas.product import ProductUpdate
from api.db.database import engine, get_db
from api.v1.models.product import Product
from api.v1.models.user import User
from api.db.database import get_db
from api.utils.dependencies import get_current_user
from uuid import UUID

# Create a router for product-related endpoints
product = APIRouter(prefix="/product", tags=["Products"])

@product.put("/{id}", response_model=ProductUpdate)
async def update_product(
    id: UUID,
    product: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the details of an existing product.

    This endpoint updates a product's attributes such as name, price, description, and tag.
    It ensures that the product exists before performing the update. The `updated_at` timestamp 
    is set to the current time to reflect when the update occurred.

    Args:
        id (UUID): The unique identifier of the product to be updated.
        product (ProductUpdate): The new product data to be updated.
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.
        db (Session): The database session, provided by the `get_db` dependency.

    Returns:
        ProductUpdate: The updated product details.

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.

    Example:
        PUT /product/123e4567-e89b-12d3-a456-426614174000
        {
            "product_name": "New Product Name",
            "price": 29.99,
            "description": "Updated description",
            "tag": "New Tag"
        }
    """
    db_product = db.query(ProductModel).filter(ProductModel.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = product.product_name
    db_product.price = product.price
    db_product.description = product.description
    db_product.tag = product.tag
    db_product.updated_at = datetime.utcnow()

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product
