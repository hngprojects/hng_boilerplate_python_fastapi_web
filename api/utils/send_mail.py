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
    admin_email = settings.MAIL_USERNAME
    user_email = context.get('email')

    admin_html = email_templates.get_template("contact_us.html").render(context)
    customer_html = email_templates.get_template("email_feedback.html").render(context)

    send_mail_handler(sender_email, admin_email, admin_html, "New Contact Request")
    send_mail_handler(admin_email, user_email, customer_html, "Thank you for contacting us")


def send_mail_handler(sender, reciever, html, subject):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = reciever

    part = MIMEText(html, "html")

    message.attach(part)

    with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.sendmail(sender, reciever, message.as_string())


def send_faq_inquiry_mail(context: dict):
    from main import email_templates
    sender_email = settings.MAIL_USERNAME
    receiver_email = context.get('email')
    password = settings.MAIL_PASSWORD
    
    html = email_templates.get_template("faq-feedback.html").render(context)

    message = MIMEMultipart("alternative")
    message["Subject"] = "We've received your inquiry"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    part = MIMEText(html, "html")

    message.attach(part)

    with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
