from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.terms import TermsAndConditions
from api.v1.schemas.terms_and_conditions import UpdateTermsAndConditions
from fastapi import HTTPException
from api.v1.models.user import User

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

    def delete(self, terms_id: str, db: Session, current_user: User):
        # Check if the terms and conditions exist
        tc = db.query(TermsAndConditions).filter(TermsAndConditions.id == terms_id).first()
        if not tc:
            raise HTTPException(status_code=404, detail="Terms and Conditions not found")

        # Delete the terms and conditions
        db.delete(tc)
        db.commit()
        return {"message": "Terms and Conditions deleted successfully", "status_code": 200, "success": True, "data": {"terms_id": terms_id}}


terms_and_conditions_service = TermsAndConditionsService()
