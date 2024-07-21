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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ProductUpdate(BaseModel):
    product_name: str
    price: float
    description: str
    tag: str

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be a positive number")
        return v

app = APIRouter()

@app.put("/api/v1/products/id", tags=['Products'])
async def update_product(
    id: int,
    product: ProductUpdate,
    token: str = Depends(oauth2_scheme)
):
    # Dummy authentication for the purpose of the example
    # actual authentication logic
    if token != "add_test_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    with Session(engine) as session:
        statement = select(Product).where(Product.id == id)
        result = session.exec(statement)
        db_product = result.first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        db_product.product_name = product.product_name
        db_product.price = product.price
        db_product.description = product.description
        db_product.tag = product.tag
        db_product.updated_date = datetime.utcnow()

        session.add(db_product)
        session.commit()
        session.refresh(db_product)

        return db_product

