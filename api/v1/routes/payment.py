from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.services.payment import PaymentService
from api.utils.dependencies import get_db
from api.v1.schemas.payment import PaymentResponse
from api.utils.db_validators import check_model_existence

payment = APIRouter(tags=['Payments'])

@payment.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, db: Session = Depends(get_db)):
    payment_service = PaymentService()
    payment = check_model_existence(db, payment_service.model, payment_id)
    return payment
