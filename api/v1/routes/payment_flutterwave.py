from fastapi import Depends, APIRouter, status, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from api.utils.success_response import success_response
from api.utils.db_validators import check_model_existence
from api.v1.schemas.payment import PaymentDetail
from api.v1.services.payment import PaymentService
from api.v1.services.user import user_service
from api.db.database import get_db
from api.v1.models import User
from decouple import config
from uuid_extensions import uuid7
import requests
from api.v1.routes.payment import payment
from api.v1.models.billing_plan import BillingPlan
from api.utils.settings import settings

@payment.post("/flutterwave", response_model=success_response)
async def pay_with_flutterwave(
    request: PaymentDetail,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    Flutterwave payment intergration - initialize payment
    """
    SECRET_KEY = settings.FLUTTERWAVE_SECRET
    FLUTTERWAVE_URL = 'https://api.flutterwave.com/v3/payments'
    header = {'Authorization': 'Bearer ' + SECRET_KEY}
    transaction_id = str(uuid7())
    plan = check_model_existence(db, BillingPlan, request.plan_id)
    data = {
        "tx_ref": transaction_id,
        "amount": float(plan.price),
        "currency": plan.currency,
        "redirect_url": request.redirect_url,
        "payment_options":"card",
        "customer":{
            "email": current_user.email
        },
    }

    try:
        response = requests.post(FLUTTERWAVE_URL, json=data, headers=header)
        response=response.json()

        # save payment detail
        payment_service = PaymentService()
        payment_data = {
            "user_id":current_user.id,
            "amount": float(plan.price),
            "currency":plan.currency,
            "status": "pending",
            "method": "card",
            "transaction_id":transaction_id
        }
        payment_service.create(db, payment_data)

        return success_response(
            status_code=status.HTTP_200_OK,
            message='Payment initiated successfully',
            data={"payment_url": response['data']['link']},
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail='Error initializing payment')
