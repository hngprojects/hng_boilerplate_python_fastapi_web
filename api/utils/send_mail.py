import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from api.utils.settings import settings

url = "deployment.api-python.boilerplate.hng.tech"
def send_magic_link(email: str, token: str):
    '''Sends magic-kink to user email'''
    sender_email = settings.MAIL_USERNAME
    receiver_email = email
    password = settings.MAIL_PASSWORD

    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Magic Link"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Use the following link to log in: http://{url}/magic-link?token={token}"
    html = f"<html><body><p>Use the following link to log in: <a href='http://{url}/verify-magic-link?token={token}'>Magic Link</a></p></body></html>"

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
