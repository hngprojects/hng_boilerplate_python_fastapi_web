from fastapi import APIRouter
from api.v1.services.payment import PaymentService
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.schemas.payment import CreatePaymentSchema

payment = APIRouter(prefix='/payments', tags=['Payment'])



@payment.post('/create', status_code=status.HTTP_201_CREATED)
async def post_single_payments(request: CreatePaymentSchema, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    print('Current User: ', current_user)
    request.user_id = current_user.id
    PaymentService.create(db, request)

    return {
        "message": "Payment successfully created",
        "success": True,
        "status": status.HTTP_201_CREATED
    }