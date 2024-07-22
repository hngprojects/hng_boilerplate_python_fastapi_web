from pydantic import EmailStr
from api.core.dependencies.email import mail_service
from fastapi import HTTPException
import logging
import smtplib

logger = logging.getLogger("waitlist")


async def send_confirmation_email(email: EmailStr, full_name: str):
    html = f"""
    <html>
    <body>
        <h1>Welcome, {full_name}!</h1>
        <p>Thank you for joining our waitlist. We'll keep you updated on our progress!</p>
        <p>Best regards,</p>
        <p>HNG BoilerPlate Team</p>
    </body>
    </html>
    """

    try:
        print(f"Attempting to send confirmation email to {email}")
        mail_service.send_mail(
            to=email, subject="Welcome to our Waitlist!", body=html)
        print(f"Confirmation email sent successfully to {email}")
    except HTTPException as e:
        print(f"Failed to send email: {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected error while sending email: {str(e)}")
        raise HTTPException(
            500, f"Failed to send confirmation email: {str(e)}")
