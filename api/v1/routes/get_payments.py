from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.utils.success_response import success_response

from api.v1.models.payment import Payment
from api.db.database import get_db
from api.v1.models.user import User
from api.v1.services.user import user_service


payments = APIRouter()


@payments.get("/payments")
def get_all_payments(db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    
    
    payments = db.query(Payment).all()
    
    return success_response(
        status_code=200,
        message= 'Records Found',
        data=payments
    )