
from fastapi import status, APIRouter,Depends
from fastapi.encoders import jsonable_encoder
from api.v1.models.subscription import Subscription
from api.v1.models.user import User 
from api.utils.json_response import JsonResponseDict
from api.utils.dependencies import get_current_user
from api.db.database import get_db
from sqlalchemy.orm import Session
from api.v1.schemas.subscription import SubscriptionRequest
from uuid import UUID

db = next(get_db())
subscription = APIRouter(prefix="/api/v1/user/subscription", tags=["Subscription"])

def send_cancellation_confirmation_notification(subscription: Subscription, db: Session):
	try:
		subscription_user = db.query(User).filter_by(id=subscription.user_id).first()
		return JsonResponseDict(
			message="Sent Subscription Cancellation Confirmation notification successfully",
			data={
					"name": subscription_user.username,
					"subscription": {
						"id": subscription.id,
						"plan": subscription.plan,
						"cancellation_date": subscription.end_date
					}
     		},
			status_code=status.HTTP_200_OK
		)
	

	except Exception as error:
		print(error)
		return JsonResponseDict(
				message="Subscription Cancellation Confirmation notification unsuccessful.",
				data={
					"success": False,
				},
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )



@subscription.post("/notification/cancellation/{subscription_id}")
def send_subscription_cancellation_confirmation(subscription_id: UUID, current_user:  User = Depends(get_current_user), db: Session = Depends(get_db)):
	try:
		invalid_request = SubscriptionRequest(id=subscription_id)
		subscription = db.query(Subscription).filter_by(id=subscription_id).first()
	except Exception as e:
		m = e.errors()
		errors = [{"field": i["loc"][0], "message": i["msg"]} for i in m]
		return JsonResponseDict(
			message="Invalid input data",
			data=jsonable_encoder({
				"status": "error",
				"errors": errors
			}),
			status_code=status.HTTP_400_BAD_REQUEST
            )

	if not subscription:
		return JsonResponseDict(
      			message="Invalid input data",
				data={
					"success": False,
					"status_code": 404
				},
				status_code=status.HTTP_404_NOT_FOUND,
        )
	if subscription.is_active == False:
		return send_cancellation_confirmation_notification(subscription=subscription, db=db)

	return JsonResponseDict(
     			message="Please check the submitted data. Subscription is active",
				content={
					"status":  "Bad Request",
				},
				status_code=status.HTTP_400_BAD_REQUEST
    )

