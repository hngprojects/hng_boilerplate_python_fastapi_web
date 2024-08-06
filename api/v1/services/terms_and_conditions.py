from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.terms import TermsAndConditions
from api.v1.schemas.terms_and_conditions import UpdateTermsAndConditions


class TermsAndConditionsService(Service):
    """Terms And conditions service."""

    def create(self):
        return super().create()

    def fetch(self, db: Session, id: str):
        tc = db.query(TermsAndConditions).filter(TermsAndConditions.id == id).first()
        if not tc:
            return None
        return tc

    def fetch_all(self):
        return super().fetch_all()

    def update(self, db: Session, id: str, data: UpdateTermsAndConditions):
        tc = db.query(TermsAndConditions).filter(TermsAndConditions.id == id).first()
        if not tc:
            return None
        if data.title:
            tc.title = data.title
        if data.content:
            tc.content = data.content
        db.commit()
        db.refresh(tc)
        return tc

    def delete(self):
        return super().delete()


terms_and_conditions_service = TermsAndConditionsService()
