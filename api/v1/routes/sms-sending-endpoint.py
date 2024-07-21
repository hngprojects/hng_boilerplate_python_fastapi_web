from twilio.rest import Client
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from fastapi import APIRouter
from hng_boilerplate_python_fastapi_web.main import app

router = APIRouter(prefix='/api/', tags=['auth'])
def send_sms(recipient_number, content):
    account_sid ="ACaaad000fe19df6daf0b7fcd3a0681664"
    auth_token = '24dc299349cb1f9f48f58cecae868fd2'
    client = Client(account_sid, auth_token)
    original_string = str(recipient_number)

    """
    replaced character is d, and it is present at the 2nd index so storing its index for future replacement
    """
    if not not recipient_number:
        return "Please provide a recipient number"
    if not content:
        return "You need to a content."
    index = 0

    # ``t`` will replace ``d`
    new_character = "+234"

    original_string = original_string[:index] + new_character + original_string[index + 1:]
    try:
        message = client.messages.create(
            to=original_string,
            body=content,
            from_="+12513192283"
        )
    except Exception as e:
        return "Something is not right!"
    else:
        return message.status


send_sms(recipient_number="08146155907", content="I love you")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SMSRequest(BaseModel):
    recipient_number: str
    content: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "fake-super-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": "authorized_user"}


@app.post("/send-sms", tags=["SMS"])
async def send_sending_endpoint(sms_request: SMSRequest, user: dict = Depends(get_current_user)):
    status = send_sms(sms_request.recipient_number, sms_request.content)
    if status == "Something is not right!":
        raise HTTPException(status_code=500, detail=status)
    return {"status": status}
