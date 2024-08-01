from api.v1.services.email_services import email_service
from api.v1.schemas.email_schema import EmailRequest
from fastapi import APIRouter, BackgroundTasks

email_sender = APIRouter(prefix='/mails', tags=["Email Template Management"])

@email_sender.post("/send-email")
async def send_email(request: EmailRequest, background_tasks: BackgroundTasks):
    '''Endpoint to send an email in the background'''

    return await email_service.send_email(
        background_tasks, 
        request.to_email, 
        request.subject, 
        request.body, 
        request.from_name
    )
