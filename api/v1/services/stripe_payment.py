from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan, UserSubscription
import stripe
from fastapi.encoders import jsonable_encoder
from api.utils.success_response import success_response
import os
from fastapi import HTTPException, status, Request
from datetime import datetime, timedelta

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def get_plan_by_name(db: Session, plan_name: str):
    return db.query(BillingPlan).filter(BillingPlan.name == plan_name).first()

def stripe_payment_request(db: Session, user_id: str, request: Request, plan_name: str):

    base_url = request.base_url

    success_url = f"{base_url}api/v1/payment/stripe/success"
    cancel_url = f"{base_url}api/v1/payment/stripe/cancel"

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan = get_plan_by_name(db, plan_name)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.name != "Free":
        try:
            # Create a checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan.currency,
                        'product_data': {
                            'name': plan.name,
                        },
                        'unit_amount': int(plan.price * 100),  # Convert to the smallest unit
                    },
                    'quantity': 1,
                }],
                mode='payment',
                customer_email=user.email,  # Automatically fill in the user's email in the checkout
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'plan_name': plan_name,
                },
            )

            if checkout_session:
                data = {
                    "cancel_url": checkout_session["cancel_url"],
                    "success_url": checkout_session["success_url"],
                    "customer_details": checkout_session["customer_details"],
                    "customer_email": checkout_session["customer_email"],
                    "created_at": checkout_session["created"],
                    "expires_at": checkout_session["expires_at"],
                    "metadata": checkout_session["metadata"],
                    "payment_method_types": checkout_session["payment_method_types"],
                    "checkout_url": checkout_session["url"],
                    "amount_total": checkout_session["amount_total"]
                }

                return success_response(
                    status_code=status.HTTP_201_CREATED,
                    message=f'payment in progress',
                    data=data,
                )

        except stripe.error.StripeError as e:
            # Handle Stripe error
            raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")

    else:
        raise HTTPException(status_code=400, detail="No payment is required for the Free plan")


def convert_duration_to_timedelta(duration: str) -> timedelta:
    if duration == "monthly":
        return timedelta(days=30)  # Approximate month length
    elif duration == "yearly":
        return timedelta(days=365)  # Approximate year length
    else:
        raise ValueError("Invalid duration")

async def update_user_plan(db: Session, user_id: str, plan_name: str):
    user = db.query(User).filter(User.id == user_id).first()
    plan = get_plan_by_name(db, plan_name)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Convert duration from string to timedelta
    try:
        duration = convert_duration_to_timedelta(plan.duration)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update the user's subscription in the database
    user_subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()

    if user_subscription:
        user_subscription.plan_id = plan.id
        user_subscription.start_date = datetime.utcnow()
        user_subscription.end_date = datetime.utcnow() + duration
    else:
        new_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + duration
        )
        db.add(new_subscription)
    
    db.commit()