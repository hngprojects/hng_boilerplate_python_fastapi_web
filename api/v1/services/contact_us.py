from api.core.base.services import Service
from typing import Optional, Any
from sqlalchemy.orm import Session
from api.v1.models.contact_us import ContactUs


class ContactUsService(Service):
    """Contact Us service functionality"""

    def create(self, db: Session, schema):
        pass

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all submisions with option to search using query parameters"""

        query = db.query(ContactUs)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(ContactUs, column) and value:
                    query = query.filter(getattr(ContactUs, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a job by id"""

        contact_us_submission = db.query(ContactUs).where(ContactUs.id == id)
        return contact_us_submission

    def fetch_by_email(self, db: Session, email: str):
        """Fetches a contact_us_submission by id"""

        contact_us_submission = db.query(ContactUs).where(ContactUs.email == email)
        return contact_us_submission

    def update(self):
        pass

    def delete(self):
        pass


contact_us_service = ContactUsService()
