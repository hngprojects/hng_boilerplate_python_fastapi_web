from typing import Any, Optional

from api.core.base.services import Service
from api.v1.models.newsletter import NewsletterSubscriber
from api.v1.schemas.newsletter import EmailSchema
from fastapi import HTTPException
from sqlalchemy.orm import Session


class NewsletterService(Service):
    """Newsletter service functionality"""

    @staticmethod
    def create(db: Session, request: EmailSchema) -> NewsletterSubscriber:
        '''add a new subscriber'''

        new_subscriber = NewsletterSubscriber(
            email=request.email)
        db.add(new_subscriber)
        db.commit()
        db.refresh(new_subscriber)

        return new_subscriber

    @staticmethod
    def check_existing_subscriber(db: Session, request: EmailSchema) -> NewsletterSubscriber:
        """
        Check if user with email already exist
        """

        newsletter = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email==request.email).first()
        if newsletter:
            raise HTTPException(
                status_code=400, detail="User already subscribed to newsletter"
            )

        return newsletter
    
    @staticmethod
    def fetch_all(db: Session, **query_params: Optional[Any]):
        '''Fetch all newsletter subscriptions with option to search using query parameters'''

        query = db.query(NewsletterSubscriber)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(NewsletterSubscriber, column) and value:
                    query = query.filter(getattr(NewsletterSubscriber, column).ilike(f'%{value}%'))

        return query.all()

    
    
    @staticmethod
    def check_nonexisting_subscriber(db: Session, request: EmailSchema):
        """As above, checks if subscription with email already exists, but raises an exception if not found.
        """        
        subscription = db.query(NewsletterSubscriber).filter(NewsletterSubscriber.email == request.email).first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscriber not found.")
        return subscription


    @staticmethod
    def delete(db: Session, request: EmailSchema) -> None:
        """
        Unsubsribes a user for newsletter
        """
        subscriber = NewsletterService.check_nonexisting_subscriber(db=db, request=request)
        db.delete(subscriber)
        db.commit
        return None
    