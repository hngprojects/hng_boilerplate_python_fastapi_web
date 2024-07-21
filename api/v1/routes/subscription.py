
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from api.v1.models.subscription import Subscription
from api.v1.models.user import User 
from typing import Annotated
from api.utils.dependencies import get_current_user
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from api.v1.schemas.subscription import SubscriptionRequest

db = next(get_db())
subscription = APIRouter(prefix="/api/v1/user/subscription", tags=["Subscription"])

def send_cancellation_confirmation_notification(subscription: Subscription, db: Session):
    try:
        subscription_user = db.query(User).filter_by(id=subscription.user_id).first()
        return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder({
                    "message": "Sent Subscription Cancellation Confirmation notification successfully",
                    "name": subscription_user.username,
                    "subscription": {
                        "id": subscription.id,
                        "plan": subscription.plan,
                        "cancellation_date": subscription.end_date
                    }
                }),) 

    except Exception as error:
        print(error)
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder({
                    "success": False,
                    "message": "Subscription Cancellation Confirmation notification unsuccessful.",
                    "status_code": 500
                }),)



@subscription.post("/notification/cancellation/{subscription_id}")
def send_subscription_cancellation_confirmation(subscription_id: str, current_user:  User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        invalid_request = SubscriptionRequest(id=subscription_id)
        subscription = db.query(Subscription).filter_by(id=subscription_id).first()
    except Exception as e:
        m = e.errors()
        errors = [{"field": i["loc"][0], "message": i["msg"]} for i in m]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({
                    "status": "error",
                    "message": "Invalid input data",
                    "errors": errors
            }))

    if not subscription:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=jsonable_encoder({
                    "success": False,
                    "message": "No Subscription Found",
                    "status_code": 404
                }),)
    if subscription.is_active == False:
        return send_cancellation_confirmation_notification(subscription=subscription, db=db)

    return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({
                    "status":  "Bad Request",
                    "message":  "Please check the submitted data. Subscription is active",
                    "status-code": 400,
            }),)

