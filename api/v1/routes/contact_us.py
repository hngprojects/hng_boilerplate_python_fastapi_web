import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, constr
from fastapi.responses import JSONResponse

# Assuming the email service is defined in services.email_service
from services.email_service import EmailService

router = APIRouter()

# Loggin setup
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

log_filename = os.path.join(log_folder, 'contact_us.log')
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
        ]
)
logger = logging.getLogger(__name__)


class ContactForm(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    message: constr(strip_whitespace=True, min_length=1)

    
@router.post("/api/v1/contact")
async def contact_us(form: ContactForm, email_service: EmailService = Depends()):
    logger.info(f"Received contact form submission: {form}")
    if email_service.send_email(form.name, form.email, form.message):
        logger.info(f"Email sent successfully for {form.email}")
        return JSONResponse(status_code=200, content={"message": "Inquiry sent successfully", "status": 200})
    else:
        logger.error(f"Failed to send inquiry for {form.email}")
        raise HTTPException(status_code=500, detail="Failed to send inquiry")
