from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
import os
from dotenv import load_dotenv
from fastapi import BackgroundTasks

load_dotenv()

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT")),
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            MAIL_STARTTLS = False,
            MAIL_SSL_TLS = True,
        )
        self.fast_mail = FastMail(self.conf)

    async def send_email(
        self, 
        background_tasks: BackgroundTasks, 
        to_email: EmailStr, 
        subject: str, 
        body: str, 
        from_name: Optional[str] = None
    ):
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body,
            subtype="plain",
            sender=f"{from_name} <{self.conf.MAIL_FROM}>" if from_name else self.conf.MAIL_FROM
        )
        
        background_tasks.add_task(self._send_email_task, message)

        return {"message": "Email sending in the background"}

    async def _send_email_task(self, message: MessageSchema):
        try:
            await self.fast_mail.send_message(message)
        except Exception as e:
            # Handle exceptions as needed
            print(f"Failed to send email: {e}")

email_service = EmailService()
