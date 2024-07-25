from fastapi import Depends, HTTPException, APIRouter, Request, Response, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.success_response import success_response
from api.v1.models.product import Product
from api.v1.schemas.user import DeactivateUserSchema, UserBase
from api.db.database import get_db
from api.v1.services.product import product_service
from api.v1.schemas.product import ProductList
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

