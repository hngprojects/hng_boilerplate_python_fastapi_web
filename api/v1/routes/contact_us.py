import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr
from fastapi.responses import JSONResponse
import requests


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactForm(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    message: constr(strip_whitespace=True, min_length=1)

def send_email_via_service(name: str, email: str, message: str) -> bool:
    url = "http://localhost:8000/api/v1/send-mail"
    headers = {
            "accept": "application/json",
            "content-type": "application/json"
    }
    data = {
            "template_id": 1,
            "recipient": email,
            "variables": {
                "name": name,
                "message": message
            }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to send email: {response.status_code}, {response.text}")
    return response.status_code == 200


@router.post("/api/v1/contact")
async def contact_us(form: ContactForm):
    logger.info(f"Received contact form submission: {form}")
    if send_email_via_service(form.name, form.email, form.message):
        logger.info(f"Email sent successfully for {form.email}")
        return JSONResponse(status_code=200, content={"message": "Inquiry sent successfully", "status": 200})
    else:
        logger.error(f"Failed to send inquiry for {form.email}")
        raise HTTPException(status_code=500, detail="Failed to send inquiry")
