from fastapi import APIRouter, status
from api.v1.schemas.products_schema import ProductSchema
from api.db.database import get_db
from api.v1.models.product import Product
from fastapi.exceptions import HTTPException
from typing import List
from uuid import UUID


product_router = APIRouter()
db = next(get_db())

@product_router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: UUID) -> ProductSchema:
    product = db.query(Product).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product no found")
    return product


@product_router.get("/", response_model=List[ProductSchema])
async def get_all_products():
    products = db.query(Product).all()
    return products
    