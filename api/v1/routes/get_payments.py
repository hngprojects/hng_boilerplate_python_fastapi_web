from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.payments import PaymentService
from api.v1.schemas.payments import PaymentsResponse

payments = APIRouter(prefix="/payments", tags=["Payments"])


@payments.get("/", response_model=list[PaymentsResponse])
async def get_all_payments(db: Session = Depends(get_db)):

    payment_service = PaymentService(db)
    all_payments = payment_service.fetch_all()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "status_code": status.HTTP_200_OK,
            "message": "Payments Record Found",
            "data": jsonable_encoder(all_payments)
        }
    )