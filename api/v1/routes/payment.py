from fastapi import APIRouter
from api.v1.services.payment import PaymentService
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status
from api.utils.dependencies import get_current_user
from api.v1.schemas.payment import PaymentSchema, CreatePaymentSchema
from api.v1.schemas.token import TokenData
from typing import List

payment = APIRouter(prefix='/payments', tags=['Payment'])


@payment.get('/{payment_id}', status_code=status.HTTP_200_OK)
async def get_single_payment(payment_id: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    payment = PaymentService.fetch(db, payment_id)
    return payment


# @payment.post('/create', status_code=status.HTTP_201_CREATED)
# async def post_single_payments(request: CreatePaymentSchema, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
#     print('Current User: ', current_user)
#     request.user_id = current_user.id
#     PaymentService.create(db, request)

#     return {
#         "message": "Payment successfully created",
#         "success": True,
#         "status": status.HTTP_201_CREATED
#     }