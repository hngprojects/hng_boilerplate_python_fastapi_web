from fastapi import Depends, status, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.customer import SuccessResponse
from api.utils.dependencies import get_current_admin
from typing import Annotated
from api.utils.json_response import JsonResponseDict

db = next(get_db())

customers = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@customers.get("", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def get_customers(
    current_user: Annotated[User, Depends(get_current_admin)], 
    limit: Annotated[int, Query(ge=1, description="Number of customers per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db)
    ):
    """
    Retrieves a paginated list of customers.

    Query parameters:
        - limit: Number of customers per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """
    if current_user.is_active == False:
        print(current_user.username)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status_code": 401,
                "message": "Forbidden",
                "error": "User is not an admin"
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

    customer_data = [
        {
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "organizations": [str(org.id) for org in customer.organizations]
        }
        for customer in customers
    ]

    data = {
        "current_page": page,
        "total_pages": total_pages,
        "limit": limit,
        "total_items": total_customers,
        "customers": customer_data
    }
    print(type(data))

    return JsonResponseDict(
            message="Fetch customer successful",
            data=data,
            status_code=status.HTTP_200_OK
        )

   