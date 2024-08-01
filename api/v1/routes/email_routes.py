
from api.v1.services.email_services import email_service
from api.v1.schemas.email_schema import EmailRequest
from typing import Optional
from fastapi import APIRouter, BackgroundTasks

email_sender = APIRouter(prefix='/mails', tags=['send email'])

@email_sender.post("/send-email")
async def send_email(request: EmailRequest, background_tasks: BackgroundTasks):
    return await email_service.send_email(background_tasks, request.to_email, request.subject, request.body, request.from_name)
