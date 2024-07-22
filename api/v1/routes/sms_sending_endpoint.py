from twilio.rest import Client
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix='/sms', tags=['auth'])
def send_sms(recipient_number: str = "+18777804236", content: str = "Default Message."):
    account_sid = 'AC8c75dc44bc4e297684e4bf64d9d62e0f'
    auth_token = '0ac58d15d8ca979e1492dc4a866c6e94'
    client = Client(account_sid, auth_token)
    # original_string = str(recipient_number)

    """
    replaced character is 0, and it is present at the 1st index so storing its index for future replacement
    """
    if not recipient_number:
        return "Please provide a recipient number"
    if not content:
        return "You need to a content."
    index = 0

    new_character = "+234"

    # original_string = original_string[:index] + new_character + original_string[index + 1:]
    try:
        message = client.messages.create(
            to=recipient_number,
            body=content,
            from_='+12513192283'
        )
    except Exception as e:
        return f"Something is not right! Error: {str(e)}"
    else:
        return message.status


class SMSRequest(BaseModel):
    recipient_number: str = '+18777804236'
    content: str = 'Hi there!'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIzYzE1OTJmZi04MTQ5LTQ3ZGYtYTVjNy1kYzRlMWExMTllM2MiLCJleHAiOjE3MjA1MzY1OTR9.rNOkbWSceAh9mEfHa_lNj89LVZ9yqTeSNydgOOQa-uU":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": "authorized_user"}


@router.post("/send", tags=["SMS"])
async def send_sending_endpoint(sms_request: SMSRequest, user: dict = Depends(get_current_user)):
    status = send_sms(sms_request.recipient_number, sms_request.content)
    if "Error" in status:
        return {
                "status": "unsuccessful",
                "status_code": 500,
                "message": "Failed to send SMS. Please try again later."
        }

    return {"status": status, "message": "SMS sent successfully", "status_code": 200}
