from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.utils.pagination import paginated_response
from api.utils.success_response import success_response
from api.v1.models.email_template import EmailTemplate
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.email_template import email_template_service
from api.v1.schemas.email_template import EmailTemplateSchema

email_template = APIRouter(prefix="/email-templates", tags=["Email Template Management"])


@email_template.get("", response_model=success_response, status_code=200)
async def get_all_email_templates(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    current_user: User = Depends(user_service.get_current_super_admin)
):
    """Endpoint to get all email templates"""

    return paginated_response(
        db=db,
        model=EmailTemplate,
        limit=limit,
        skip=skip,
    )


@email_template.post("", response_model=success_response, status_code=201)
async def create_email_template(
    schema: EmailTemplateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to create a new email template. Only accessible to superadmins"""

    template = email_template_service.create(db, schema=schema)

    return success_response(
        data=jsonable_encoder(template),
        message="Successfully created email template",
        status_code=status.HTTP_201_CREATED,
    )


@email_template.get("/{template_id}", response_model=success_response, status_code=200)
async def get_single_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to get a single template"""

    template = email_template_service.fetch(db, template_id=template_id)

    return success_response(
        data=jsonable_encoder(template),
        message="Successfully fetched email template",
        status_code=status.HTTP_200_OK,
    )


@email_template.patch("/{template_id}", response_model=success_response, status_code=200)
async def update_template(
    template_id: str,
    schema: EmailTemplateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to update a single template"""

    template = email_template_service.update(db, template_id=template_id, schema=schema)

    return success_response(
        data=jsonable_encoder(template),
        message="Successfully updated template",
        status_code=status.HTTP_200_OK,
    )


@email_template.delete("/{template_id}", status_code=204)
async def delete_email_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to delete a single template"""

    email_template_service.delete(db, template_id=template_id)


@email_template.post("/{template_id}/send", response_model=success_response, status_code=200)
async def send_email_template(
    template_id: str,
    recipient_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(user_service.get_current_super_admin),
):
    """Endpoint to send an email template to a recipient"""

    send_result = email_template_service.send(db=db, template_id=template_id, recipient_email=recipient_email)

    if send_result["status"] == "failure":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=send_result["message"])

    return success_response(
        data=send_result,
        message=f"Email sent successfully to {recipient_email}",
        status_code=status.HTTP_200_OK,
    )
