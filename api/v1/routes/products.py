from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.role import ResponseModel
from api.v1.schemas.product import ProductStock
from api.v1.models.product import Product
from api.v1.models.permission import Permission
from api.utils.dependencies import get_current_admin
import uuid
from api.utils.dependencies import get_current_admin
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from api.v1.models.user import User, WaitlistUser
from typing import Annotated

product = APIRouter(prefix="/products", tags=["Products"])


@product.get("/{productId}/stock", status_code=200)
async def get_product_stock(
    current_admin: Annotated[User, Depends(get_current_admin)],
    productId: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Fetches the current stock level for a specific product.

    Args:
        productId (str): The ID of the product.

    Returns:
        ProductStock: The current stock level of the product.

    Raises:
        HTTPException: If the product is not found.
    """
    db_product = db.query(Product).filter(Product.productId == productId).first()
    if not db_product:
        raise HTTPException(status_code=400, message="Bad Request")

    prod = ProductStock(
        productId=db_product.productId,
        currentStock=db_product.currentStock,
        lastUpdated=db_product.lastUpdated,
    )

    return prod
