from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from aiosmtplib import send
from email.message import EmailMessage

app = FastAPI()

# Email configuration
EMAIL = "project-test@hng.email"
PASSWORD = "j*orWasSatc^TrdT7k7BGZ#"
SMTP_HOST = "work.timbu.cloud"
SMTP_PORT = 465

# Define a Pydantic model for the request body
class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str = "Test Email"
    body: str = "This is a test email from FastAPI"



@app.post("/send-tinbu-mail")
async def send_email(email_request: EmailRequest):
    # Create the email message
    message = EmailMessage()
    message["From"] = EMAIL
    message["To"] = email_request.to_email
    message["Subject"] = email_request.subject
    message.set_content(email_request.body)

    # SMTP configuration
    smtp_settings = {
        "hostname": SMTP_HOST,
        "port": SMTP_PORT,
        "username": EMAIL,
        "password": PASSWORD,
        "use_tls": True,  # Use SSL/TLS for secure connection
    }

    try:
        # Send the email
        await send(message, **smtp_settings)
        return {"message": f"Email sent to {email_request.to_email} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
