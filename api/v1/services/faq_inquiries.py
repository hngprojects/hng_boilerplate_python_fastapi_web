from fastapi import Depends
from api.core.base.services import Service
from api.v1.models.faq_inquiries import FAQInquiries
from api.v1.schemas.faq_inquiries import CreateFAQInquiry
from sqlalchemy.orm import Session
from typing import Annotated, Optional, Any
from api.v1.routes.faq_inquiries import get_db


class FAQInquiryService(Service):
    """FAQ Inquiry Service."""

    def __init__(self) -> None:
        self.adabtingMapper = {
            "full_name": "full_name",
            "email": "email",
            "message": "message",
        }
        super().__init__()

    # ------------ CRUD functions ------------ #
    # CREATE
    def create(self, db: Annotated[Session, Depends(get_db)], data: CreateFAQInquiry):
        """Create a new FAQ Inquiry."""
        faq_inquiry = FAQInquiries(
            full_name=getattr(data, self.adabtingMapper["full_name"]),
            email=getattr(data, self.adabtingMapper["email"]),
            message=getattr(data, self.adabtingMapper["message"]),
        )
        db.add(faq_inquiry)
        db.commit()
        db.refresh(faq_inquiry)
        return faq_inquiry

    # READ
    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all submisions with option to search using query parameters"""

        query = db.query(FAQInquiries)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(FAQInquiries, column) and value:
                    query = query.filter(getattr(FAQInquiries, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a faq_inquiry by id"""

        faq_inquiry = db.query(FAQInquiries).get(id)
        return faq_inquiry

    def fetch_by_email(self, db: Session, email: str):
        """Fetches a faq_inquiry by email"""

        faq_inquiry = db.query(FAQInquiries).filter(FAQInquiries.email == email).first()
        return faq_inquiry
    
    def delete(self, db: Session, id: str):
        """Delete a faq_inquiry by id"""

        faq_inquiry = db.query(FAQInquiries).get(id)
        db.delete(faq_inquiry)
        db.commit()
        return faq_inquiry
    
    def update(self, db: Session, id: str, data: CreateFAQInquiry):
        faq_inquiry = db.query(FAQInquiries).get(id)
        faq_inquiry.full_name = data.full_name
        faq_inquiry.email = data.email
        faq_inquiry.message = data.message
        db.commit()
        db.refresh(faq_inquiry)
        return faq_inquiry


faq_inquiries_service = FAQInquiryService()