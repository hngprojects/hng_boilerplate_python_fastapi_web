from pydantic import EmailStr
from api.core.dependencies.email import mail_service


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
    mail_service.send_mail(email, "Welcome to our Waitlist!", html)
