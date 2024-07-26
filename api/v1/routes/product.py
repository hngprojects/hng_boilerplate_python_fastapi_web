from fastapi import Depends, HTTPException, APIRouter, Request, Response, status, Query
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime


from api.utils.success_response import success_response
from api.v1.models.product import Product
from api.v1.schemas.user import DeactivateUserSchema, UserBase
from api.db.database import get_db
from api.v1.services.product import product_service
from api.v1.schemas.product import ProductList
from api.v1.schemas.product import ProductUpdate, ResponseModel
from api.utils.dependencies import get_current_user
from api.v1.services.user import user_service
from api.v1.models import User

product = APIRouter(prefix='/products', tags=['Products'])

@product.get('/{org_id}', status_code=status.HTTP_200_OK, response_model=ProductList)
def get_organization_products(
    org_id: str,
    current_user: Annotated[User, Depends(user_service.get_current_user)],
    limit: Annotated[int, Query(ge=1, description="Number of products per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db), 
    ):
    '''
    Endpoint to retrieve a paginated list of products of an organization.

    Query parameter: 
        - limit: Number of product per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    '''

    products = product_service.fetch_by_organization(db, user=current_user, org_id=org_id, limit=limit, page=page)

    total_products = len(products)

    total_pages = int(total_products / limit) + (total_products % limit > 0)

    product_data = [
        {
            "name": product.name,
            "description": product.description,
            "price": str(product.price)
        }
        for product in products
    ]

    data = {
        "current_page": page,
        "total_pages": total_pages,
        "limit": limit,
        "total_items": total_products,
        "products": product_data
    }

    return success_response(
        status_code=200, 
        message="Successfully fetched organizations products", 
        data=data
        )






@product.put("/{id}", response_model=ResponseModel)
async def update_product(
    id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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
    try:
        updated_product = product_service.update(db, id=str(id), schema=product_update)
    except HTTPException as e:
        raise e

    # Prepare the response
    response = ResponseModel(
        success=True,
        status_code=200,
        message="Product updated successfully",
        data={
            "id": updated_product.id,
            "name": updated_product.name,
            "price": updated_product.price,
            "description": updated_product.description,
            "updated_at": updated_product.updated_at
        }
    )
    
    return response

