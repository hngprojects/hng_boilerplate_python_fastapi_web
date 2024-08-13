from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan, UserSubscription
from api.v1.models.organisation import Organisation
import stripe
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, join
from fastapi.encoders import jsonable_encoder
from api.utils.success_response import success_response
import os
from fastapi import HTTPException, status, Request
from datetime import datetime, timedelta

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def get_all_plans(db: Session):
    """
    Retrieve all billing plan details.
    """
    try:
        data = db.query(BillingPlan).all()
        if not data:
            raise HTTPException(status_code=404, detail="No billing plans found")
        return success_response(status_code=status.HTTP_200_OK, message="Plans successfully retrieved", data=data)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching billing plans")


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
                    status_code=status.HTTP_200_OK,
                    message='payment in progress',
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
    # Fetch the user by ID
    user = db.query(User).filter(User.id == user_id).first()

    # Fetch the plan by name
    plan = get_plan_by_name(db, plan_name)

    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the plan exists
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Convert duration from string to timedelta
    try:
        duration = convert_duration_to_timedelta(plan.duration)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch the organisation ID from the plan
    organisation_id = plan.organisation_id

    # Update the user's subscription in the database
    user_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.organisation_id == organisation_id
    ).first()

    if user_subscription:
        user_subscription.plan_id = plan.id
        user_subscription.start_date = datetime.utcnow()
        user_subscription.end_date = datetime.utcnow() + duration
    else:
        user_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            organisation_id=organisation_id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + duration
        )
        db.add(user_subscription)

    # Commit the transaction
    db.commit()
    db.refresh(user_subscription)  # Refresh the session to get the updated data

    # Return the updated or newly created subscription
    return user_subscription


def fetch_all_organisations_with_users_and_plans(db: Session):
    # Perform a join to retrieve the relevant data
    stmt = (
        select(
            Organisation.id,
            Organisation.name,
            User.id.label("user_id"),
            (User.first_name + " " + User.last_name).label("user_name"),
            BillingPlan.name.label("plan_name"),
            BillingPlan.price,
            BillingPlan.currency,
            BillingPlan.duration,
            UserSubscription.start_date,
            UserSubscription.end_date
        )
        .join(UserSubscription, Organisation.id == UserSubscription.organisation_id)
        .join(User, User.id == UserSubscription.user_id)
        .join(BillingPlan, BillingPlan.id == UserSubscription.plan_id)
    )

    result = db.execute(stmt).all()

    # Organize the data by organizations, users, and their plans
    organizations_data = {}
    for row in result:
        org_id = row.id
        if org_id not in organizations_data:
            organizations_data[org_id] = {
                "organisation_name": row.name,
                "users": []
            }

        user_info = {
            "user_id": row.user_id,
            "user_name": row.user_name,
            "plan_name": row.plan_name,
            "price": row.price,
            "currency": row.currency,
            "duration": row.duration,
            "start_date": row.start_date,
            "end_date": row.end_date
        }

        organizations_data[org_id]["users"].append(user_info)

    return list(organizations_data.values())