from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.faq import FAQ
from api.v1.schemas.faq import CreateFAQ, UpdateFAQ
from api.utils.db_validators import check_model_existence


class FAQService(Service):
    '''FAQ service functionality'''

    def create(self, db: Session, schema: CreateFAQ):
        """Create a new FAQ"""

        new_faq = FAQ(**schema.model_dump())
        db.add(new_faq)
        db.commit()
        db.refresh(new_faq)

        return new_faq

    def fetch_all_grouped_by_category(self, db: Session, **query_params: Optional[Any]):
        """Fetch all FAQs grouped by category"""
        query = db.query(FAQ.category, FAQ.question, FAQ.answer)

        if query_params:
            for column, value in query_params.items():
                if hasattr(FAQ, column) and value:
                    query = query.filter(
                        getattr(FAQ, column).ilike(f"%{value}%"))
        faqs = query.order_by(FAQ.category).all()

        grouped_faqs = {}
        for faq in faqs:
            if faq.category not in grouped_faqs:
                grouped_faqs[faq.category] = []
            grouped_faqs[faq.category].append(
                {"question": faq.question, "answer": faq.answer})

        return grouped_faqs

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all FAQs with option to search using query parameters"""

        query = db.query(FAQ)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(FAQ, column) and value:
                    query = query.filter(
                        getattr(FAQ, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, faq_id: str):
        """Fetches a, FAQ by id"""

        faq = check_model_existence(db, FAQ, faq_id)
        return faq

    def update(self, db: Session, faq_id: str, schema: UpdateFAQ):
        """Updates an FAQ"""

        faq = self.fetch(db=db, faq_id=faq_id)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(faq, key, value)

        db.commit()
        db.refresh(faq)
        return faq

    def delete(self, db: Session, faq_id: str):
        """Deletes an FAQ"""

        faq = self.fetch(db=db, faq_id=faq_id)
        db.delete(faq)
        db.commit()


faq_service = FAQService()
