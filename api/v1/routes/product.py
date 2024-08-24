from fastapi import Depends, APIRouter, status, Query, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Annotated
from typing import List, Optional

from api.utils.pagination import paginated_response
from api.utils.success_response import success_response
from api.db.database import get_db
from api.v1.models.product import Product, ProductFilterStatusEnum, ProductStatusEnum
from api.v1.services.product import product_service, ProductCategoryService
from api.v1.schemas.product import (
    ProductCategoryCreate,
    ProductCategoryData,
    ProductCreate,
    ProductList,
    ProductUpdate,
    ResponseModel,
    ProductStockResponse,
    ProductFilterResponse,
    SuccessResponse,
    ProductCategoryRetrieve,
    ProductDetail,
)
from api.utils.dependencies import get_current_user
from api.v1.services.user import user_service
from api.v1.models import User

non_organisation_product = APIRouter(prefix="/products", tags=["Products"])


@non_organisation_product.get("", response_model=success_response, status_code=200)
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


# categories
@non_organisation_product.post("/categories", status_code=status.HTTP_201_CREATED)
def create_product_category(
    category_schema: ProductCategoryCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Endpoint to create a product category

    Args:
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.
        db (Session): The database session, provided by the `get_db` dependency.

    Returns:
        ResponseModel: The created product category

    Raises:
        HTTPException: 401 FORBIDDEN (Current user is not a authenticated)
    """

    new_category = ProductCategoryService.create(
        db, category_schema, current_user)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Category successfully created",
        data=jsonable_encoder(new_category),
    )


@non_organisation_product.get(
    "/categories", response_model=success_response, status_code=200
)
def retrieve_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """
    Retrieve all product categories from database
    """

    categories = ProductCategoryService.fetch_all(db)

    categories_filtered = list(
        map(lambda x: ProductCategoryRetrieve.model_validate(x), categories)
    )

    if len(categories_filtered) == 0:
        categories_filtered = [{}]

    return success_response(
        message="Categories retrieved successfully",
        status_code=200,
        data=jsonable_encoder(categories_filtered),
    )


product = APIRouter(
    prefix="/organisations/{org_id}/products", tags=["Products"])


# create
@product.post("", status_code=status.HTTP_201_CREATED)
def product_create(
    org_id: str,
    product: ProductCreate,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Session = Depends(get_db),
):
    created_product = product_service.create(
        db=db, schema=product, org_id=org_id, current_user=current_user
    )

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Product created successfully",
        data=jsonable_encoder(created_product),
    )


# Retrive detail
@product.get(
    "/{product_id}",
    response_model=dict[str, int | str | bool | ProductDetail],
    summary="Get product detail",
    description="Endpoint to get detail about the product with the given `id`",
)
async def get_product_detail(
    org_id: str,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """
    Retrieve product detail

    This endpoint retrieve details about a product

    Args:
        org_id (UUID): The unique identifier of the organisation
        product_id (UUID): The unique identifier of the product to be retrieved.
        db (Session): The database session, provided by the `get_db` dependency.
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.

    Returns:
        ProductDetail: The detail of the product matching the given id

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.
    """

    product = product_service.fetch_single_by_organisation(
        db, org_id, product_id, current_user
    )

    return {
        "status_code": status.HTTP_200_OK,
        "success": True,
        "message": "Product fetched successfully",
        "data": product,
    }


# Update
@product.put("/{product_id}", response_model=ResponseModel)
async def update_product(
    org_id: str,
    product_id: str,
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
        db,
        product_id=product_id,
        schema=product_update,
        org_id=org_id,
        current_user=current_user,
    )

    # Prepare the response
    return success_response(
        status_code=200,
        message="Product updated successfully",
        data=jsonable_encoder(updated_product),
    )


# delete
@product.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    org_id: str,
    product_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Enpoint to delete a product

    Args:
        product_id (str): The unique identifier of the product to be deleted
        current_user (User): The currently authenticated user, obtained from the `get_current_user` dependency.
        db (Session): The database session, provided by the `get_db` dependency.

    Raises:
        HTTPException: 401 FORBIDDEN (Current user is not a authenticated)
        HTTPException: 404 NOT FOUND (Product to be deleted cannot be found)
    """

    product_service.delete(
        db=db, org_id=org_id, product_id=product_id, current_user=current_user
    )


@product.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ProductList,
)
def get_organisation_products(
    org_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    limit: Annotated[int, Query(
        ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(
        ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db),
):
    """
    Endpoint to retrieve a paginated list of products of an organisation.

    Query parameter:
        - limit: Number of product per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """

    products = product_service.fetch_by_organisation(
        db, user=current_user, org_id=org_id, limit=limit, page=page
    )

    return success_response(
        status_code=200,
        message="Successfully fetched organisations products",
        data=[jsonable_encoder(product) for product in products],
    )


@product.get("/{product_id}/stock", response_model=ResponseModel)
async def get_product_stock(
    product_id: str,
    org_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    db: Session = Depends(get_db),
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
    stock_info = product_service.fetch_stock(
        db=db, product_id=product_id, current_user=current_user, org_id=org_id
    )
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product stock fetched successfully",
        data=jsonable_encoder(stock_info),
    )


@product.get(
    "/filter-status",
    response_model=SuccessResponse[List[ProductFilterResponse]],
    status_code=200,
)
async def get_products_by_filter_status(
    org_id: str,
    filter_status: ProductFilterStatusEnum = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get products by filter status"""
    try:
        products = product_service.fetch_by_filter_status(
            db=db, org_id=org_id, filter_status=filter_status
        )
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
    org_id: str,
    status: ProductStatusEnum = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Endpoint to get products by status"""
    try:
        products = product_service.fetch_by_status(
            db=db, org_id=org_id, status=status)
        return SuccessResponse(
            message="Products retrieved successfully", status_code=200, data=products
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve products")


@product.get("/search", status_code=status.HTTP_200_OK, response_model=ProductList)
def search_products(
    org_id: str,
    name: Optional[str] = Query(None, description="Search by product name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(
        None, description="Filter by minimum price"),
    max_price: Optional[float] = Query(
        None, description="Filter by maximum price"),
    limit: Annotated[int, Query(
        ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(
        ge=1, description="Page number (starts from 1)")] = 1,
    current_user: Annotated[User, Depends(
        user_service.get_current_user)] = None,
    db: Session = Depends(get_db),
):
    """
    Endpoint to search for products with optional filters and pagination.

    Query parameters:
        - name: Search by product name
        - category: Filter by category
        - min_price: Filter by minimum price
        - max_price: Filter by maximum price
        - limit: Number of products per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """

    products = product_service.search_products(
        db=db,
        org_id=org_id,
        name=name,
        category=category,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        page=page,
    )

    return success_response(
        status_code=200,
        message="Products searched successfully",
        data=[jsonable_encoder(product) for product in products],
    )
