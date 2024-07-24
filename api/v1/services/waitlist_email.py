from pydantic import EmailStr
from api.core.dependencies.email import mail_service
from fastapi import HTTPException
from api.utils.logger import logger


async def send_confirmation_email(email: EmailStr, full_name: str):
    plain_text_body = "Welcome, {}. Thank you for joining our waitlist. We'll keep you updated \
    on our progress! Best regards, HNG BoilerPlate Team".format(full_name)

    try:
        logger.info(f"Attempting to send confirmation email to {email}") 
        mail_service.send_mail(to=email, subject="Welcome to our Waitlist!", body=plain_text_body)
        logger.info(f"Confirmation email sent successfully to {email}")  
    except HTTPException as e:
        logger.warning(f"Failed to send email: {e.detail}") 
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {str(e)}")  
        raise HTTPException(status_code=500, detail=f"Failed to send confirmation email: {str(e)}")
