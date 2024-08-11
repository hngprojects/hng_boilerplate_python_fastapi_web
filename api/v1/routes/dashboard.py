from fastapi import APIRouter, Depends, status
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
from typing import Annotated
from fastapi.security import OAuth2
from datetime import datetime, timedelta
from api.v1.services.user import oauth2_scheme
from api.v1.services.analytics import analytics_service, AnalyticsServices


dashboard = APIRouter(prefix="/dashboard", tags=['Dashboard'])


def get_current_month_date_range():
    now = datetime.utcnow()
    start_date = datetime(now.year, now.month, 1)
    end_date = (start_date + timedelta(days=32)
                ).replace(day=1) - timedelta(seconds=1)
    return start_date, end_date


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


@dashboard.get('/statistics', status_code=status.HTTP_200_OK)
async def get_analytics_summary(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    analytics_service: Annotated[AnalyticsServices, Depends()],
    start_date: datetime = None,
    end_date: datetime = None
):
    """
    Retrieves analytics summary data for an organisation or super admin.
    Args:
        token: access_token
        db: database Session object
        start_date: start date for filtering
        end_date: end date for filtering
    Returns:
        analytics response: contains the analytics summary data
    """
    if not start_date or not end_date:
        start_date, end_date = get_current_month_date_range()
    return analytics_service.get_analytics_summary(token=token, db=db, start_date=start_date, end_date=end_date)
