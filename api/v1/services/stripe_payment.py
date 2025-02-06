from sqlalchemy.orm import Session
from api.v1.models.user import User
from api.v1.models.billing_plan import BillingPlan, UserSubscription
from api.v1.models.organisation import Organisation
from api.v1.models.payment import Payment
import stripe
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, join
from fastapi.encoders import jsonable_encoder
from api.utils.success_response import success_response, fail_response
import os
from sqlalchemy import cast, DateTime
from fastapi import HTTPException, status, Request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')



def get_plan_by_id(db: Session, plan_id: str):
    return db.query(BillingPlan).filter(BillingPlan.id == plan_id).first()


def convert_duration_to_timedelta(duration: str) -> timedelta:
    if duration == "monthly":
        return timedelta(days=30)  # Approximate month length
    elif duration == "yearly":
        return timedelta(days=365)  # Approximate year length
    else:
        raise ValueError("Invalid duration")
    
def is_eligible_for_plan(db: Session, user_id: str, plan_id: str):
    # Fetch the user's current subscription
    user_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id
    ).first()

    # If the user has no subscription, they are eligible for the plan
    if not user_subscription:
        return True

    # Check if the user's current subscription has ended
    if user_subscription.end_date < datetime.utcnow():
        return True

    # If the user is trying to upgrade or downgrade, they are eligible
    if user_subscription.plan_id != plan_id:
        return True

    # If none of the above conditions are met, the user is not eligible
    return False


def calculate_prorated_amount(db: Session, user_id: str, plan_id: str):
    # Fetch the user's current subscription
    user_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id
    ).first()

    # Fetch the plan the user is trying to upgrade or downgrade to
    plan = get_plan_by_id(db, plan_id)

    # Calculate the number of days remaining in the current subscription
    days_remaining = (user_subscription.end_date - datetime.utcnow()).days

    # Calculate the total number of days in the current subscription
    total_days = (user_subscription.end_date - user_subscription.start_date).days

    # Calculate the prorated amount
    prorated_amount = (plan.price / total_days) * days_remaining

    return prorated_amount


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


async def update_user_plan(db: Session, user_id: str, plan_id: str, is_downgrade: bool = False):
    user = db.query(User).filter(User.id == user_id).first()
    plan = get_plan_by_id(db, plan_id)

    try:
        duration = convert_duration_to_timedelta(plan.duration)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user_subscription = db.query(UserSubscription).filter(
        UserSubscription.user_id == user_id
    ).first()

    if user_subscription:
        old_plan = user_subscription.billing_plan
        old_duration = convert_duration_to_timedelta(user_subscription.billing_plan.duration)
        days_remaining = (datetime.strptime(user_subscription.end_date, "%Y-%m-%d %H:%M:%S.%f") - datetime.utcnow()).days
        total_days = (datetime.strptime(user_subscription.end_date, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(user_subscription.start_date, "%Y-%m-%d %H:%M:%S.%f")).days

        prorated_amount = 0  # Initialize prorated_amount to 0
        if is_downgrade:
            prorated_amount = (old_plan.price / total_days) * days_remaining
            #TODO Refund or credit the user's account (implement based on  payment logic)
        else:
            prorated_amount = (plan.price - prorated_amount)
            #TODO Charge the user's payment method (implement based on  payment logic)

        user_subscription.plan_id = plan.id
        user_subscription.start_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
        user_subscription.end_date = (datetime.utcnow() + duration).strftime("%Y-%m-%d %H:%M:%S.%f")
        user_subscription.billing_cycle = datetime.utcnow() + duration
        
    else:
        user_subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            organisation_id=plan.organisation_id,
            start_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f"),
            end_date=(datetime.utcnow() + duration).strftime("%Y-%m-%d %H:%M:%S.%f"),
            billing_cycle=datetime.utcnow() + duration
        )
        db.add(user_subscription)

    db.commit()
    db.refresh(user_subscription)
    return user_subscription


def stripe_payment_request(db: Session, user_id: str, request: Request, plan_id: str):

    # base_urls = request.base_url
    # base_urls = str(request.url.scheme) + "://" + str(request.url.netloc)
    
    base_urls = "https://anchor-python.teams.hng.tech/"
    success_url = f"{base_urls}payment" + "/success?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = f"{base_urls}payment/pricing"

    # success_url = f"{base_urls}api/v1/payment/stripe" + "/success?session_id={CHECKOUT_SESSION_ID}"
    # cancel_url = f"{base_urls}api/v1/payment/stripe/cancel"


    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return fail_response(status_code=404, message="User not found")

    plan = get_plan_by_id(db, plan_id)

    if not plan:
        return fail_response(status_code=404, message="Plan not found")
    

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
                    'plan_id': plan.id,
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
        return fail_response(status_code=400, message="No payment is required for the Free plan")



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