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
from api.utils.auth import get_current_user






Product = APIRouter(prefix="/api/v1", tags=["Products"])


@Product.put("/products/id", response_model=ProductUpdate)
async def update_product(
    id: int,
    product: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_product = db.query(ProductModel).filter(ProductModel.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.product_name = product.product_name
    db_product.price = product.price
    db_product.description = product.description
    db_product.tag = product.tag
    db_product.updated_date = datetime.utcnow()

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product
