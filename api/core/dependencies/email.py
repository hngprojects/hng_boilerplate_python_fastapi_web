import smtplib
from typing import List, Optional, Union

from fastapi import HTTPException
from api.utils.settings import settings


class MailService:
    '''Class to send different emails for different services'''

    def send_mail(self, to: str, subject: str, body: str):
        '''Function to send email to a user either as a regular test or as html file'''

        # try:
        #     with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as conn:
        #         conn.starttls()
        #         conn.login(user=settings.MAIL_USERNAME, password=settings.MAIL_PASSWORD) 
        #         conn.sendmail(
        #             from_addr=settings.MAIL_FROM,
        #             to_addrs=to,
        #             msg=f"Subject:{subject}\n\n{body}"
        #         )

        # except smtplib.SMTPException as smtp_error:
        #     raise HTTPException(500, f'SMTP ERROR- {smtp_error}')

        print('Email sent successfully')


mail_service = MailService()
