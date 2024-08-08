from fastapi import APIRouter, Depends, Query, status, HTTPException
from api.db.database import get_db
from sqlalchemy.orm import Session
from typing import Annotated

from api.v1.models import User
from api.v1.services.user import user_service
from api.v1.services.product import product_service
from api.utils.pagination import get_pagination_details
from api.utils.success_response import success_response
from api.v1.schemas.dashboard import (
    DashboardProductCountResponse,
    DashboardSingleProductResponse,
    DashboardProductListResponse
)


dashboard = APIRouter(prefix="/dashboard", tags=['Dashboard'])


@dashboard.get("/products/count", response_model=DashboardProductCountResponse)
async def get_all_products_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin)
):
    """
    Endpoint to retrieve all products COUNT, from the dashboard, by ``superadmin``.
    """
    num_of_products = len(product_service.fetch_all(db))

    if not num_of_products:
        # RETURN nothing found message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Products not found"
        )

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Products count fetched successfully",
        data={"count": num_of_products}
    )
    

@dashboard.get("/products", response_model=DashboardProductListResponse)
async def get_all_products(
    current_user: User = Depends(user_service.get_current_super_admin),
    limit: Annotated[int, Query(ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve a paginated list of products, from the dashboard, by ``superadmin``.

    Query parameter:
        - limit: Number of payment per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """
    # GET offset from page and limit
    offset = (page - 1) * limit

    # FETCH all products
    products = product_service.fetch_and_dictize(
        db=db, dynamic=True, offset=offset, limit=limit)

    # GET number of products
    num_of_products = len(products)

    if not num_of_products:
        # RETURN not found message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Products not found"
        )

    # GATHER all data in a dict
    data = {
        "products": products,
        "pagination": get_pagination_details(num_of_products, limit, offset)
    }

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Products fetched successfully",
        data=data
    )
    

@dashboard.get("/products/{product_id}", response_model=DashboardSingleProductResponse)
async def get_single_product(
    product_id: str,
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve a single product, from the dashboard, by ``superadmin``.
    """
    prod_detail = product_service.dynamic_product_dict(db=db, product_or_id=product_id)

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product fetched successfully",
        data=prod_detail
    )