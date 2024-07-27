from fastapi import Depends, status, APIRouter, HTTPException, Header
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.customer import CustomerUpdate, SuccessResponse
from api.utils.dependencies import get_super_admin
from api.v1.services.customers import CustomerServices
from typing import Annotated, Optional

customers = APIRouter(prefix="/customers", tags=["customers"])


@customers.put("/{customer_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    Authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Updates customer details for a given customer ID.
    - customer_id: ID of the customer to update.
    - customer_data: New data for the customer.
    """

    # Extract the token from the Authorization header
    try:
        if not Authorization:
            raise IndexError
        token = Authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Use the token to check if the user is a super admin
    get_super_admin(db=db, token=token)


    # Fetch the customer and profile from the database
    customer_services = CustomerServices()

    customer = customer_services.get_user(db, customer_id)
    customer_profile = customer_services.get_user_profile(db, customer_id)

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    if not customer_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found.")

    # Update customer details
    if customer_data.first_name:
        customer.first_name = customer_data.first_name
    if customer_data.last_name:
        customer.last_name = customer_data.last_name
    if customer_data.email:
        customer.email = customer_data.email
    if customer_data.username:
        customer.username = customer_data.username
    if customer_data.phone_number:
        customer_profile.phone_number = customer_data.phone_number

    db.commit()

    return SuccessResponse(
        status_code=200,
        message="Customer details updated successfully.",
        data={
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone_number": customer_profile.phone_number,
            "username": customer.username
        }
    )
