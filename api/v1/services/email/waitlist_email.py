from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from api.utils.settings import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)


async def send_confirmation_email(email: str, full_name: str):
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

    message = MessageSchema(
        subject="Welcome to our Waitlist!",
        recipients=[email],
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
