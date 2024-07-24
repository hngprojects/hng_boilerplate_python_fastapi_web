from sqlalchemy.orm import Session

from api.v1.models.contact_us import ContactUs
from api.v1.schemas.contact_us import ContactUsCreate


class ContactUsService:
    """Service class for handling contact messages."""

    @staticmethod
    def create_contact_message(
        db: Session,
        contact_us: ContactUsCreate,
    ) -> ContactUs:
        """Creates and saves a contact message to the database."""
        db_contact_us = ContactUs(**contact_us.model_dump())
        db.add(db_contact_us)
        db.commit()
        db.refresh(db_contact_us)
        return db_contact_us
