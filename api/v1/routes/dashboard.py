from fastapi import status, APIRouter, Path, Depends
from sqlalchemy.orm import Session
from api.utils.success_response import success_response
from typing import Annotated
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.product import product_service
from fastapi.encoders import jsonable_encoder


dashboard = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard.get(
    "/products/{id}",
    summary="Get single product",
    description="Get the detail of a single product",
)
async def get_product(
    id: Annotated[str, Path()],
    db: Session = Depends(get_db),
    _: User = Depends(user_service.get_current_user),
):
    """
    Get detail about a single product

    This endpoint returns detailed information about a product with the provided `product_id`

    Args:
        id (UUID): The unique identifier of the product to be retrieved.
        db (Session): The database session, provided by the `get_db` dependency.
        _ (User): The currently authenticated user, obtained from the `get_current_user` dependency.

    Returns:
        Product data

    Raises:
        HTTPException: If the product with the specified `id` does not exist, a 404 error is raised.

    Example:
        curl --location 'http://localhost:7001/api/v1/dashboard/products/840d1d3f-f3b6-4ee7-aa08-e6b31793a224' --header 'Authorization: Bearer <access_token>'
    """

    product = product_service.fetch(db, id)
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Product fetched successfully",
        data=jsonable_encoder(product),
    )
