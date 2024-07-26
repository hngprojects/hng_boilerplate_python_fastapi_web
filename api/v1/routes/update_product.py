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
from api.v1.services.product import product_service
from api.v1.models.user import User
from api.utils.dependencies import get_current_user
from uuid import UUID
from api.utils.config import SECRET_KEY, ALGORITHM
import jwt





# Create a router for product-related endpoints
productupdate = APIRouter(prefix="/products", tags=["Products"])

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
    try:
        updated_product = product_service.update(db=db, id=str(id), schema=product_update)
    except HTTPException as e:
        raise e

    # Prepare the response
    response = ResponseModel(
        success=True,
        status_code=200,
        message="Product updated successfully",
        data={
            "id": updated_product.id,
            "name": updated_product.name,
            "price": updated_product.price,
            "description": updated_product.description,
            "updated_at": updated_product.updated_at
        }
    )
    
    return response
