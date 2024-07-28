from fastapi import APIRouter, HTTPException, status
from api.v1.schemas.sms_twilio import SMSRequest
from api.v1.services.sms_twilio import send_sms
from api.utils.success_response import success_response

sms = APIRouter(prefix="/sms/send", tags=["sms"])

@sms.post("/", status_code=status.HTTP_200_OK, response_model=dict)
def send_sms_endpoint(sms_request: SMSRequest):
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
        print("🇦🇱", result['sid'])
        return success_response(
            status_code=200,
            message = "SMS sent successfully.", 
            data = {
                "sid": result['sid']
            } 
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions for custom error messages
        raise e
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "unsuccessful",
                "status_code": 500,
                "message": "Failed to send SMS. Please try again later."
            }
        )
