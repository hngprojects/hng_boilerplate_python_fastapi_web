from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional, Any
from api.core.base.services import Service
from api.v1.routes.contact_us import get_db
from api.v1.schemas.contact_us import CreateContactUs
from api.v1.models import ContactUs


class ContactUsService(Service):
    """Contact Us Service."""

    def __init__(self) -> None:
        self.adabtingMapper = {
            "full_name": "full_name",
            "email": "email",
            "title": "phone_number", # Adapting the schema to the model
            "message": "message",
            "org_id": "org_id",
        }
        super().__init__()

    # ------------ CRUD functions ------------ #
    # CREATE
    def create(self, db: Annotated[Session, Depends(get_db)], data: CreateContactUs):
        """Create a new contact us message."""
        contact_message = ContactUs(
            full_name=getattr(data, self.adabtingMapper["full_name"]),
            email=getattr(data, self.adabtingMapper["email"]),
            title=getattr(data, self.adabtingMapper["title"]),
            message=getattr(data, self.adabtingMapper["message"]),
            # org_id=getattr(data, self.adabtingMapper["org_id"])
        )
        db.add(contact_message)
        db.commit()
        db.refresh(contact_message)
        return contact_message

    # READ
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

    # UPDATE
    def update(self, db: Annotated[Session, Depends(get_db)], contact_id: int, data: CreateContactUs):
        """Update a single contact us message."""
        pass

    # DELETE
    def delete(self, db: Annotated[Session, Depends(get_db)], contact_id: int):
        """Delete a single contact us message."""
        pass


contact_us_service = ContactUsService()
