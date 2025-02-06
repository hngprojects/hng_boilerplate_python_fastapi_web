from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.email_template import EmailTemplate
from api.v1.schemas.email_template import EmailTemplateSchema
from api.utils.db_validators import check_model_existence
import logging
import time



class EmailTemplateService(Service):
    '''Email template service functionality'''

    def create(self, db: Session, schema: EmailTemplateSchema):
        """Create a new Email Template"""
        new_template = EmailTemplate(**schema.model_dump())
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        return new_template

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all email templates with option to search using query parameters"""

        query = db.query(EmailTemplate)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(EmailTemplate, column) and value:
                    query = query.filter(getattr(EmailTemplate, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, template_id: str):
        """Fetches a template by id"""

        email_template = check_model_existence(db, EmailTemplate, template_id)
        return email_template

    def update(self, db: Session, template_id: str, schema: EmailTemplateSchema):
        """Updates an email template"""

        template = self.fetch(db=db, template_id=template_id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(template, key, value)

        db.commit()
        db.refresh(template)
        return template

    def delete(self, db: Session, template_id: str):
        """Deletes an FAQ"""

        template = self.fetch(db=db, template_id=template_id)
        db.delete(template)
        db.commit()
        
    
    def send(self, db: Session, template_id: str, recipient_email: str, max_retries: int = 3):
        """Send an email template to a recipient with error handling and retries"""
        
        template = self.fetch(db=db, template_id=template_id)

        for attempt in range(max_retries):
            try:
                self._send_email(recipient_email, template)
                logging.info(f"Template {template_id} sent successfully to {recipient_email}")
                return {"status": "success", "message": f"Email sent to {recipient_email}"}
            
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed to send template {template_id}: {e}")
                time.sleep(2 ** attempt)

        logging.error(f"All attempts to send template {template_id} to {recipient_email} failed.")
        return {"status": "failure", "message": "Failed to send email after multiple attempts"}

    def _send_email(self, recipient_email: str, template: EmailTemplate):
        """Mock email sending function"""
        if not recipient_email or not template:
            raise ValueError("Invalid recipient email or template.")
        pass

email_template_service = EmailTemplateService()
