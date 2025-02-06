from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from api.utils.settings import settings
from premailer import transform



async def send_email(
    recipient: str, 
    template_name: str, 
    subject: str, 
    context: Optional[dict] = None
):
    from main import email_templates

    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        MAIL_STARTTLS = False,
        MAIL_SSL_TLS = True,
        MAIL_FROM_NAME='HNG Boilerplate',
        # SUPPRESS_SEND=True  # suppress sending of email in testing environment
    )
    
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        subtype=MessageType.html
    )
    
    # Render the template with context
    html = email_templates.get_template(template_name).render(context)
    message.body = transform(html)
    
    fm = FastMail(conf)
    await fm.send_message(message)
    