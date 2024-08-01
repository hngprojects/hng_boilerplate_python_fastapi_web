from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.email_template import EmailTemplate
from api.v1.schemas.email_template import EmailTemplateSchema
from api.utils.db_validators import check_model_existence


class EmailTemplateService(Service):
    '''Email template service functionality'''

    def create(self, db: Session, schema: EmailTemplateSchema):
        """Create a new FAQ"""

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

    def update(self, db: Session, template_id: str, schema: EmailTemplate):
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


email_template_service = EmailTemplateService()
