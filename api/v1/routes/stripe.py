from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe
from api.v1.services.stripe_payment import stripe_payment_request, update_user_plan, fetch_all_organisations_with_users_and_plans
import json
from api.v1.schemas.stripe import PlanUpgradeRequest
from typing import List
from api.db.database import get_db
import os
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.user import user_service
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

subscription_ = APIRouter(prefix="/payment", tags=["subscribe-plan"])

@subscription_.post("/stripe/upgrade-plan")
def stripe_payment(
    plan_upgrade_request: PlanUpgradeRequest, 
    request: Request, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(user_service.get_current_user)
    ):
    return stripe_payment_request(db, plan_upgrade_request.user_id, request, plan_upgrade_request.plan_name) 

@subscription_.get("/stripe/success")
def success_upgrade():
    return {"message" : "Payment successful"}

@subscription_.get("/stripe/cancel")
def cancel_upgrade():
    return {"message" : "Payment canceled"}

@subscription_.post("/webhook")
async def webhook_received(
    request: Request, 
    db: Session = Depends(get_db)
    ):

    payload = await request.body()
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    if event["type"] == "checkout.session.completed":
        payment = event["data"]["object"]
        response_details = {
            "amount": payment["amount_total"],
            "currency": payment["currency"],
            "user_id": payment["metadata"]["user_id"],
            "user_email": payment["customer_details"]["email"],
            "user_name": payment["customer_details"]["name"],
            "order_id": payment["id"]
        }
        # Save to DB
        # Send email in background task
        await update_user_plan(db, payment["metadata"]["user_id"], payment["metadata"]["plan_name"])
        return {"message": response_details}
    

@subscription_.get("/organisations/users/plans")
async def get_organisations_with_users_and_plans(db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_super_admin)):
    try:
        data = fetch_all_organisations_with_users_and_plans(db)
        if not data:
            return {"status_code": 404, "success": False, "message": "No data found"}
        return success_response(
            status_code=status.HTTP_302_FOUND,
            message='billing details successfully retrieved',
            data=data,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))