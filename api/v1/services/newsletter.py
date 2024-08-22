from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.schemas.newsletter import EmailSchema
from api.core.base.services import Service
from api.v1.models.newsletter import NewsletterSubscriber, Newsletter
from typing import Optional, Any, Annotated
from api.utils.db_validators import check_model_existence
from api.utils.success_response import success_response
from api.v1.schemas.newsletter import SingleNewsletterResponse

class NewsletterService(Service):
    """Newsletter service functionality"""

    @staticmethod
    def create(db: Session, request: EmailSchema) -> NewsletterSubscriber:
        """add a new subscriber"""

        new_subscriber = NewsletterSubscriber(email=request.email)
        db.add(new_subscriber)
        db.commit()
        db.refresh(new_subscriber)

        return new_subscriber

    @staticmethod
    def check_existing_subscriber(
        db: Session, request: EmailSchema
    ) -> NewsletterSubscriber:
        """
        Check if user with email already exist
        """

        newsletter = (
            db.query(NewsletterSubscriber)
            .filter(NewsletterSubscriber.email == request.email)
            .first()
        )
        if newsletter:
            return newsletter

    @staticmethod
    def fetch(db: Session, id: str):
        """Fetches a single newsletter by id"""
        return check_model_existence(db=db, model=Newsletter, id=id)

    @staticmethod
    def fetch_all(db: Session, **query_params: Optional[Any]):
        """Fetch all newsletter subscriptions with option to search using query parameters"""

        query = db.query(NewsletterSubscriber)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(NewsletterSubscriber, column) and value:
                    query = query.filter(
                        getattr(NewsletterSubscriber, column).ilike(f"%{value}%")
                    )

        return query.all()

    @staticmethod
    def unsubscribe(db: Session, request: EmailSchema) -> None:
        '''Unsubscribe a user from the newsletter'''
        newsletter_subscriber = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == request.email).first()
        if not newsletter_subscriber:
            raise HTTPException(
                status_code=400,
                detail="No active subscription found for your email."
            )
        db.delete(newsletter_subscriber)
        db.commit()

    def delete(db: Session, id: str):
        """Deletes a single newsletter by id"""

        newsletter = check_model_existence(db=db, model=Newsletter, id=id)

        db.delete(newsletter)
        db.commit()
    
    @staticmethod
    def update(db: Session, id: str, schema):
        """Updates the newsletter with id"""
        newsletter = check_model_existence(db=db, model=Newsletter, id=id)
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(newsletter, key, value)
        db.commit()
        db.refresh(newsletter)
        return newsletter
        db.commit()
