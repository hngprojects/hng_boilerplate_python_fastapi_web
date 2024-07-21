from fastapi import APIRouter, status, Depends
from api.v1.schemas.products_schema import ProductSchema
from api.db.database import get_db
from api.v1.models.product import Product
from api.v1.models.user import User
from api.v1.schemas.token import TokenData
from api.utils.config import ALGORITHM, SECRET_KEY
from api.utils.dependencies import get_current_user
from fastapi.exceptions import HTTPException
from typing import List
from uuid import UUID

db = next(get_db())
product_router = APIRouter(prefix="/api/v1/products", tags=["auth"])


@product_router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: UUID, current_user: TokenData = Depends(get_current_user)) -> ProductSchema:
    product = db.query(Product).get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product no found")
    return product


@product_router.get("/", response_model=List[ProductSchema])
async def get_all_products():
    products = db.query(Product).all()
    return products
    