from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.schemas.customer import CustomerUpdate, SuccessResponse
from api.utils.dependencies import get_super_admin
from typing import Annotated

customers = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@customers.put("/{customer_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    current_user: Annotated[User, Depends(get_super_admin)],
    db: Session = Depends(get_db)
):
    """
    Updates customer details for a given customer ID.
    - customer_id: ID of the customer to update.
    - customer_data: New data for the customer.
    """

    # Fetch the customer from the database
    customer = db.query(User).filter(User.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid customer ID.")

    # Update customer details
    customer.first_name = customer_data.first_name
    customer.last_name = customer_data.last_name
    customer.email = customer_data.email
    customer.phone_number = customer_data.phone
    customer.address = customer_data.address

    db.commit()

    return SuccessResponse(
        status_code=200,
        message="Customer details updated successfully.",
        data={
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone_number": customer.phone_number,
            "address": customer.address
        }
    )
