from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.services.payment import PaymentService
from api.utils.dependencies import get_db
from api.v1.schemas.payment import PaymentResponse

payment = APIRouter()

@payment.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment_service = PaymentService()
    payment = payment_service.get_payment_by_id(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Not Found")
    return payment
