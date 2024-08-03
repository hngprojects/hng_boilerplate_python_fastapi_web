from fastapi import APIRouter, status, Header, Depends
from api.v1.schemas.contact import AdminGet200Response, AdminGet200Data, AdminGet200ResponseAllMessage
from typing import Optional
from api.utils.dependencies import get_super_admin
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.contact import ContactMessage
from api.v1.services.user import user_service
from api.v1.models.user import User

contact = APIRouter(prefix="", tags=['contact'])


@contact.get('/contacts', response_model=AdminGet200ResponseAllMessage, status_code=status.HTTP_200_OK)
def get_all_contacts(
        org_id: str,
        current_admin: User = Depends(user_service.get_current_super_admin),
        db: Session = Depends(get_db),
):
    contact_message = ContactMessage()

    contact_message.check_admin_access(db, current_admin.id, org_id)

    messages = contact_message.fetch_all_messages(db, org_id)

    if not messages:
        contact_message.raise_not_found()

    response_data = contact_message.get_response_data(messages)

    response_body = AdminGet200ResponseAllMessage(data=response_data)

    return response_body


@contact.get('/contact/{id}', response_model=AdminGet200Response, status_code=status.HTTP_200_OK)
def get_contact(
        id: str,
        current_admin: User = Depends(user_service.get_current_super_admin),
        db: Session = Depends(get_db),
):

    contact_message = ContactMessage()

    message = contact_message.fetch_message(db, id)

    contact_message.check_admin_access(db, current_admin.id, message.org_id)

    if not message:
        contact_message.raise_not_found()

    response_data = AdminGet200Data(full_name=message.full_name,
                                    email=message.email,
                                    title=message.title,
                                    message=message.message
                                    )

    response_body = AdminGet200Response(data=response_data.__dict__)

    return response_body
