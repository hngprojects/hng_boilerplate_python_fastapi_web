from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.v1.services.payment import PaymentService
from api.utils.dependencies import get_db
from api.v1.schemas.payment import PaymentResponse

payment = APIRouter(tags=['Payments'])

@payment.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment_service = PaymentService()
    payment = payment_service.get_payment_by_id(db, payment_id)
    return payment
