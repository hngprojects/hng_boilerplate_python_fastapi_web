#!/usr/bin/env python3
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from pydantic import BaseModel, validator
from fastapi.security import OAuth2PasswordBearer

from api.db.database import engine, get_db
from api.v1.models.product import Product
from api.v1.utils.auth import get_current_user





Product = APIRouter(prefix="/api/v1", tags=["Roles"])



@Product.put("/api/v1/products/{id}", tags=['Products'])
async def update_product(
    id: int,
    product: ProductUpdate,
    current_user: User = Depends(get_current_user),  # Use the authentication dependency
    db: Session = Depends(get_db)
):
    # Find the product to update
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product details
    db_product.product_name = product.product_name
    db_product.price = product.price
    db_product.description = product.description
    db_product.tag = product.tag
    db_product.updated_date = datetime.utcnow()

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product
