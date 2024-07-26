from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.product import DashboardProductData, DashboardProductResponse
from api.v1.services.product import product_service
from api.v1.services.user import user_service

dashboard = APIRouter(prefix="/dashboard", tags=['Dashboard'])
# product_service = ProductService()

@dashboard.get("/products/{product_id}", response_model=DashboardProductResponse)
async def get_product_dashboard(
    product_id: str = Path(..., regex="^[0-9]+$"),
    current_user: User = Depends(user_service.get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific product by its ID for the dashboard.

    This endpoint is only accessible to superadmins. It fetches the details of a product
    from the database and returns them in a structured response.

    Args:
        product_id (str): The ID of the product to retrieve.
        current_user (User): The current authenticated user (injected by dependency).
        db (Session): The database session (injected by dependency).

    Returns:
        ProductResponse: A response containing the product data, status code, and a message.

    Raises:
        HTTPException: 
            - 403 error if the user is not a superadmin.
            - 404 error if the product is not found.
    """
    # Check if the user is a superadmin
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are NOT authorized to access this endpoint"
        )
    
    product = product_service.fetch(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    return DashboardProductResponse(
        status_code=status.HTTP_200_OK,
        message="Product retrieved successfully",
        data=DashboardProductData.model_validate(product)
    )
