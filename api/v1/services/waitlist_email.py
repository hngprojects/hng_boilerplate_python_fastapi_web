from pydantic import EmailStr
from api.core.dependencies.email_sender import send_email
from api.core.dependencies.google_email import mail_service
from fastapi import HTTPException
from api.utils.logger import logger
from sqlalchemy.orm import Session
from api.v1.models.waitlist import Waitlist


async def send_confirmation_email(email: EmailStr, full_name: str):
    plain_text_body = "Welcome, {}. Thank you for joining our waitlist. We'll keep you updated \
    on our progress! Best regards, HNG BoilerPlate Team".format(
        full_name
    )

    try:
        logger.info(f"Attempting to send confirmation email to {email}")
        mail_service.send_mail(
            to=email, subject="Welcome to our Waitlist!", body=plain_text_body
        )
        logger.info(f"Confirmation email sent successfully to {email}")
    except HTTPException as e:
        logger.warning(f"Failed to send email: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to send confirmation email: {str(e)}"
        )


def add_user_to_waitlist(db: Session, email: str, full_name: str):
    """Adds a user to the waitlist."""
    db_user = Waitlist(email=email, full_name=full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def find_existing_user(db: Session, email: str):
    """Finds an existing user by email."""
    return db.query(Waitlist).filter(Waitlist.email == email).first()
