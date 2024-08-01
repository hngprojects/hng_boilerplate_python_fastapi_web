# from mailjet_rest import Client
# import os
# from dotenv import load_dotenv
# from fastapi import APIRouter, HTTPException, Response
# from pydantic import BaseModel, EmailStr
# from api.utils.success_response import success_response
# from typing import Optional 

# # Load environment variables from .env file
# load_dotenv()

# email_sender = APIRouter(prefix='/mailjet', tags=['send email'])

# class MailjetService:
#     def __init__(self):
#         self.api_key = os.getenv('MAILJET_API_KEY') 
#         self.api_secret = os.getenv('MAILJET_API_SECRET')
#         self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
#         self.hard_coded_from_email = "michael@wave38.onmicrosoft.com"

#     def send_mail(self, to_email: str, subject: str, text_part: str, from_name: str = None, to_name: str = None, html_part: str = None):
#         data = {
#             'Messages': [
#                 {
#                     "From": {
#                         "Email": self.hard_coded_from_email,
#                         "Name": from_name if from_name else self.hard_coded_from_email.split('@')[0]
#                     },
#                     "To": [
#                         {
#                             "Email": to_email,
#                             "Name": to_name if to_name else to_email.split('@')[0]
#                         }
#                     ],
#                     "Subject": subject,
#                     "TextPart": text_part,
#                 }
#             ]
#         }
        
#         if html_part:
#             data['Messages'][0]['HTMLPart'] = html_part
        
#         result = self.mailjet.send.create(data=data)
        
#         if result.status_code != 200:
#             raise HTTPException(status_code=result.status_code, detail=result.json())
        
#         return result.json()

# mailjet_service = MailjetService()

# # Request model for the API endpoint
# class EmailRequest(BaseModel):
#     to_email: EmailStr
#     subject: str
#     text_part: str
#     from_name: Optional[str] = None
#     to_name: Optional[str] = None
#     html_part: Optional[str] = None

# # API endpoint to send an email
# @email_sender.post("/send-email/")
# def send_email(request: EmailRequest):
#     response = mailjet_service.send_mail(
#         to_email=request.to_email,
#         subject=request.subject,
#         text_part=request.text_part,
#         from_name=request.from_name,
#         to_name=request.to_name,
#         html_part=request.html_part
#     )
#     send_emails_ = success_response(200, "Message sent successfully", response)
#     return send_emails_