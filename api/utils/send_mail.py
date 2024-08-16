import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api.utils.settings import settings


async def send_magic_link(context: dict):
    """Sends magic-kink to user email"""
    from main import email_templates
    sender_email = settings.MAIL_USERNAME
    receiver_email = context.get('email')
    password = settings.MAIL_PASSWORD
    
    html = email_templates.get_template("signin.html").render(context)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Magic Link"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    part = MIMEText(html, "html")

    message.attach(part)

    with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


async def send_contact_mail(context: dict):
    """Sends user contact to admin mail

    Args:
        context (dict): Holds data for sending email, such as 'name', 'email', and 'message'.
    """
    from main import email_templates
    sender_email = settings.MAIL_FROM
    reciever_email = settings.MAIL_USERNAME
    password = settings.MAIL_PASSWORD

    html = email_templates.get_template("contact_us.html").render(context)

    message = MIMEMultipart("alternative")
    message["Subject"] = "New Contact Request"
    message["From"] = sender_email
    message["To"] = reciever_email

    part = MIMEText(html, "html")

    message.attach(part)

    with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.login(settings.MAIL_USERNAME, password)
        server.sendmail(sender_email, reciever_email, message.as_string())


