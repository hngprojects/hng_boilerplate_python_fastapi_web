from sqlalchemy.orm import Session
from api.v1.models import ContactUs


class ContactService:
    @staticmethod
    def get_all_contact_messages(db: Session):
        """
        Fetch all contact messages from the database
        """
        return db.query(ContactUs).all()
