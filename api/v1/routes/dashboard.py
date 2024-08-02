from fastapi import APIRouter, Depends
from api.db.database import get_db
from sqlalchemy.orm import Session

from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.product import product_service
from api.utils.success_response import success_response
from api.v1.schemas.dashboard import (
    DashboardProductCountResponse,
    DashboardSingleProductResponse,
    DashboardProductListResponse
)


dashboard = APIRouter(prefix="/dashboard", tags=['Dashboard'])


@dashboard.get("/products/count", response_model=DashboardProductCountResponse)
async def get_products_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    products = product_service.fetch_all(db)

    return success_response(
        status_code=200,
        message="Products count fetched successfully",
        data={"count": len(products)}
    )
    

@dashboard.get("/products", response_model=DashboardProductListResponse)
async def get_products(
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db)
):
    products = product_service.fetch_all(db)

    payment_data = [
        {
            "name": prod.name,
            "description": prod.description,
            "price": str(prod.price),
            "category": prod.category.name,
            "quantity": prod.quantity,
            "image_url": prod.image_url,
            "archived": prod.archived,
            "created_at": prod.created_at.isoformat(),
        }
        for prod in products
    ]

    return success_response(
        status_code=200,
        message="Products fetched successfully",
        data=payment_data
    )
    

@dashboard.get("/products/{product_id}", response_model=DashboardSingleProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db)
):
    prod = product_service.fetch(db, product_id)

    return success_response(
        status_code=200,
        message="Product fetched successfully",
        data={
            "name": prod.name,
            "description": prod.description,
            "price": str(prod.price),
            "category": prod.category.name,
            "quantity": prod.quantity,
            "image_url": prod.image_url,
            "archived": prod.archived,
            "created_at": prod.created_at.isoformat(),
        }
    )