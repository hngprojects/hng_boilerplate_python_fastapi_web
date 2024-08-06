from fastapi import Depends, APIRouter, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Annotated
from typing import List

from api.utils.pagination import paginated_response
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.models.product import Product, ProductFilterStatusEnum, ProductStatusEnum
from api.v1.services.product import product_service, ProductCategoryService
from api.v1.schemas.product import (
    ProductCreate,
    ProductList,
    ProductUpdate,
    ResponseModel,
    ProductStockResponse,
    ProductFilterResponse,
    SuccessResponse,
    ProductCategoryRetrieve
)
from api.utils.dependencies import get_current_user
from api.v1.services.user import user_service
from api.v1.models import User

product = APIRouter(prefix="/products", tags=["Products"])


@product.post("/{org_id}", status_code=status.HTTP_201_CREATED)
def product_create(
    org_id: str,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    created_product = product_service.create(
        db=db, schema=product, org_id=org_id, current_user=current_user
    )

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Product created successfully",
        data=jsonable_encoder(created_product),
    )


@product.get("", response_model=success_response, status_code=200)
async def get_all_products(
    current_user: Annotated[User, Depends(user_service.get_current_super_admin)],
    limit: Annotated[int, Query(
        ge=1, description="Number of products per page")] = 10,
    skip: Annotated[int, Query(
        ge=1, description="Page number (starts from 1)")] = 0,
    db: Session = Depends(get_db),
):
    """Endpoint to get all products. Only accessible to superadmin"""

    return paginated_response(db=db, model=Product, limit=limit, skip=skip)


@product.get(
    "/filter-status",
    response_model=SuccessResponse[List[ProductFilterResponse]],
    status_code=200,
)
async def get_products_by_filter_status(
    filter_status: ProductFilterStatusEnum = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get products by filter status"""
    try:
        products = product_service.fetch_by_filter_status(db, filter_status)
        return SuccessResponse(
            message="Products retrieved successfully", status_code=200, data=products
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve products")


@product.get(
    "/status",
    response_model=SuccessResponse[List[ProductFilterResponse]],
    status_code=200,
)
async def get_products_by_status(
    status: ProductStatusEnum = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get products by status"""
    try:
        products = product_service.fetch_by_status(db, status)
        return SuccessResponse(
            message="Products retrieved successfully", status_code=200, data=products
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve products")


@product.get("/categories", response_model=success_response, status_code=200)
def retrieve_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """
    Retrieve all product categories from database
    """

    categories = ProductCategoryService.fetch_all(db)

    categories_filtered = list(
        map(lambda x: ProductCategoryRetrieve.model_validate(x), categories))

    if (len(categories_filtered) == 0):
        categories_filtered = [{}]

    return success_response(
        message="Categories retrieved successfully",
        status_code=200,
        data=jsonable_encoder(categories_filtered)
    )


@product.get("/{org_id}", status_code=status.HTTP_200_OK, response_model=ProductList)
@product.get(
    "/organizations/{org_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductList,
)
def get_organization_products(
    org_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    limit: Annotated[int, Query(
        ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(
        ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db),
):
    """
    Endpoint to retrieve a paginated list of products of an organization.

    Query parameter:
        - limit: Number of product per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """

    products = product_service.fetch_by_organization(
        db, user=current_user, org_id=org_id, limit=limit, page=page
    )

    total_products = len(products)

    total_pages = int(total_products / limit) + (total_products % limit > 0)

    product_data = [
        {
            "name": product.name,
            "description": product.description,
            "price": str(product.price),
        }
        for product in products
    ]

    data = {
        "current_page": page,
        "total_pages": total_pages,
        "limit": limit,
        "total_items": total_products,
        "products": product_data,
    }

    return success_response(
        status_code=200,
        message="Successfully fetched organizations products",
        data=data,
    )


@product.get("/{id}/stock", response_model=ResponseModel)
async def get_product_stock(
    id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Retrieve the current stock level for a specific product.

    This endpoint fetches the current stock information for a given product,
    including the total stock across all variants and the last update time.

    Args:
        id (str): The unique identifier of the product.
        db (Session): The database session, provided by the `get_db` dependency.


    Returns:
        ResponseModel: A success response containing the product stock information.

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.
    """
    stock_info = product_service.fetch_stock(db, id, current_user)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product stock fetched successfully",
        data=jsonable_encoder(stock_info),
    )


@product.put("/{id}", response_model=ResponseModel)
async def update_product(
    id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the details of an existing product.

    This endpoint updates a product's attributes such as name, price, description, and tag.
    It ensures that the product exists before performing the update. The `updated_at` timestamp
    is set to the current time to reflect when the update occurred.

    Args:
        id (UUID): The unique identifier of the product to be updated.
        product (ProductUpdate): The new product data to be updated.
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.
        db (Session): The database session, provided by the `get_db` dependency.

    Returns:
        ProductUpdate: The updated product details.

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.

    Example:
        PUT /product/123e4567-e89b-12d3-a456-426614174000
        {
            "name": "New Product Name",
            "price": 29.99,
            "description": "Updated description",
        }
    """

    updated_product = product_service.update(
        db, id=str(id), schema=product_update)

    # Prepare the response
    return success_response(
        status_code=200,
        message="Product updated successfully",
        data=jsonable_encoder(updated_product),
    )
