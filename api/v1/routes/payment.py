from fastapi import Depends, APIRouter, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from api.utils.success_response import success_response
from api.v1.schemas.payment import PaymentListResponse, PaymentResponse
from api.v1.services.payment import PaymentService
from api.v1.services.user import user_service
from api.db.database import get_db
from api.v1.models import User

payment = APIRouter(prefix="/transactions", tags=["Transactions"])

payment_service = PaymentService()

@payment.get(
    "/current-user", status_code=status.HTTP_200_OK, response_model=PaymentListResponse
)
def get_payments_for_current_user(
    current_user: User = Depends(user_service.get_current_user),
    limit: Annotated[int, Query(ge=1, description="Number of payments per page")] = 10,
    page: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1,
    db: Session = Depends(get_db),
):
    """
    Endpoint to retrieve a paginated list of payments of ``current_user``.

    Query parameter:
        - limit: Number of payment per page (default: 10, minimum: 1)
        - page: Page number (starts from 1)
    """
    

    # FETCH all payments for current user
    payments = payment_service.fetch_by_user(
        db, user_id=current_user.id, limit=limit, page=page
    )

    # GET number of payments
    num_of_payments = len(payments)

    if not num_of_payments:
        # RETURN not found message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payments not found for user"
        )

    # GET total number of pages based on number of payments/limit per page
    total_pages = int(num_of_payments / limit) + (num_of_payments % limit > 0)

    # COMPUTE payment data into a list
    payment_data = [
        {
            "amount": str(pay.amount),
            "currency": pay.currency,
            "status": pay.status,
            "method": pay.method,
            "created_at": pay.created_at.isoformat(),
        }
        for pay in payments
    ]

    # GATHER all data in a dict
    data = {
        "pagination": {
            "limit": limit,
            "current_page": page,
            "total_pages": total_pages,
            "total_items": num_of_payments,
        },
        "payments": payment_data,
        "user_id": current_user.id,
    }

    # RETURN all data with success message
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Payments fetched successfully",
        data=data,
    )

@payment.get("/user/{user_id}", response_model=success_response, status_code=status.HTTP_200_OK)
def get_user_payments_by_id(
    user_id : str,
    current_user : Annotated[User , Depends(user_service.get_current_user)],
    db : Annotated[Session, Depends(get_db)],
    page_size: Annotated[int, Query(ge=1, description="Number of payments per page")] = 10,
    page_number: Annotated[int, Query(ge=1, description="Page number (starts from 1)")] = 1
    ):
    """Functions that handles get all transactions for a user by id with endpoint

    Args:
        user_id (str): Identifier of the user
        current_user (Annotated[User , Depends): Dependency to get the current User
        page_size (Annotated[int, Query, optional): The total amount of instances to be returned per page. Defaults to 1, description="Number of payments per page")]=10.
        page_number (Annotated[int, Query, optional): page number to be viewed. Defaults to 1, description="Page number (starts from 1)")]=1.

        
    """
    payments = payment_service.fetch_by_user(
        db=db,
        user_id=user_id,
        limit=page_size,
        page=page_number
        )
    return success_response(
        status_code=status.HTTP_200_OK,
        message='Payments retrieved',
        data=[jsonable_encoder(payment) for payment in payments]
    )


@payment.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    '''
    Endpoint to retrieve a payment by its ID.
    '''
    payment = payment_service.get_payment_by_id(db, payment_id)
    return payment

