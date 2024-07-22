from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session


from api.v1.models.product import Product
from api.v1.schemas.product_create import ProductCreate, SuccessResponse, ErrorResponse, ProductResponse
from api.db.database import get_db
from api.utils.dependencies import get_current_user
from datetime import datetime


product_create = APIRouter(prefix="/api/v1/products", tags=["products"])

# Add products


@product_create.post("/", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    # Create a new product instance
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Prepare response data
    response_data = ProductResponse(
        name=db_product.name,
        description=db_product.description,
        price=db_product.price,
        created_at=db_product.created_at,
        updated_at=db_product.updated_at
    )
    if db_product:
        return SuccessResponse(
            status="success",
            message="Product created successfully",
            data=response_data
        )
    else:
        return ErrorResponse(
            status_code=401,
            status="Failed",
            message="Server Error",
            errors=response_data
        )
