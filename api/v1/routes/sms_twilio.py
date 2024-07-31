from fastapi import APIRouter, HTTPException, status, Depends
from api.v1.schemas.sms_twilio import SMSRequest
from api.v1.services.sms_twilio import send_sms
from api.utils.success_response import success_response
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.utils.dependencies import get_current_user
from typing import Annotated

sms = APIRouter(prefix="/sms/send", tags=["SMS"])

@sms.post("/", status_code=status.HTTP_200_OK, response_model=SMSRequest)
def send_sms_endpoint(
    sms_request: SMSRequest,
    current_user: Annotated[User, Depends(user_service.get_current_user)],

    ):
    """
    Endpoint to send SMS using Twilio.
    
    Parameters:
        sms_request (SMSRequest): The request body containing phone number and message.
        
    Returns:
        dict: The response containing status and message SID or error details.
    """
    try:
        result = send_sms(sms_request.phone_number, sms_request.message)

        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "unsuccessful",
                    "status_code": 500,
                    "message": "Failed to send SMS. Please try again later."
                }
            )
        return success_response(
            status_code=200,
            message = "SMS sent successfully.", 
            data = {
                "sid": result['sid']
            } 
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unsuccessful",
                "status_code": 500,
                "message": "Failed to send SMS. Please try again later."
            }
        )