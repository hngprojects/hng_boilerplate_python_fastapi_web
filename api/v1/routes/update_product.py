#!/usr/bin/env python3
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from pydantic import BaseModel, validator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from api.v1.models.product import Product as ProductModel
from api.v1.schemas.product import ProductUpdate, ResponseModel
from api.db.database import engine, get_db
from api.v1.models.product import Product
from api.v1.models.user import User
from api.utils.dependencies import get_current_user
from uuid import UUID
from api.utils.config import SECRET_KEY, ALGORITHM
import jwt





# Create a router for product-related endpoints
productupdate = APIRouter(prefix="/product", tags=["Products"])

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
            "name": "New Product Name",
            "price": 29.99,
            "description": "Updated description",
        }
    """

    

@productupdate.put("/{id}", response_model=ResponseModel)
async def update_product(
    id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    # Convert id to UUID
    try:
        id = UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Retrieve the product from the database using the provided ID
    db_product = db.query(ProductModel).filter(ProductModel.id == str(id)).first()
    
    # If the product is not found, raise a 404 HTTPException
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product's fields with the values from the request
    db_product.name = product_update.name
    db_product.price = product_update.price
    db_product.description = product_update.description
    db_product.updated_at = datetime.utcnow()  

    # Add the updated product back to the session
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Response
    response = ResponseModel(
        success=True,
        status_code=200,
        message="Product updated successfully",
        data={
            "id": db_product.id,
            "name": db_product.name,
            "price": db_product.price,
            "description": db_product.description,
            "updated_at": db_product.updated_at
        }
    )

    return response
