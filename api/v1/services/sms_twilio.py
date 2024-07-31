from twilio.rest import Client
from api.utils.settings import settings

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_sms(phone_number: str, message: str):
    try:
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return {"status": "success", "sid": message.sid}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    