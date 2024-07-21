from fastapi import Depends, status, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.customer import SuccessResponse
from api.utils.dependencies import get_current_user
from typing import Annotated

db = next(get_db())

customers = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@customers.get("", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def get_customers(
    current_user: Annotated[User, Depends(get_current_user)], 
    db: Session = Depends(get_db), 
    limit: int = Query(default=10, ge=1, description="Number of customers per page"),
    page: int = Query(default=1, ge=1, description="Page number (starts from 1)")
    ):
    """
    Retrieves a paginated list of customers.

    Query parameters:
        - limit: Number of customers per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """
    # Checking if the user is active and an admin
    if current_user.is_admin == False or current_user.is_active == False:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status_code": 401,
                "message": "Unauthorized",
                "error": "Bad Request"
            }
        )

    # Calculating offset value from page number and limit given
    offset_value = (page - 1) * limit

    # Querying the db for users without the role admin set to true
    customers = db.query(User).filter(User.is_admin == False).offset(offset_value).limit(limit).all()

    # Total number of customers
    total_customers = len(customers)

    # Total pages: integer division with ceiling for remaining items
    total_pages = int(total_customers / limit) + (total_customers % limit > 0)

    data = [
        {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "organizations": [org.id for org in customer.organizations]
        }
        for customer in customers
    ]

    # Response data
    response = SuccessResponse(
        status_code=200,
        current_page=page,
        total_pages=total_pages,
        limit=limit,
        total_items=total_customers,
        data=data
    )

    return response
    