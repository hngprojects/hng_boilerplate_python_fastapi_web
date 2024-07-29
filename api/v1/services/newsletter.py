from fastapi import HTTPException
from sqlalchemy.orm import Session
from api.v1.schemas.newsletter import EmailSchema
from api.core.base.services import Service
from api.v1.models.newsletter import Newsletter
from typing import Optional, Any

class NewsletterService(Service):
    '''Newsletter service functionality'''

    @staticmethod
    def create(db: Session, request: EmailSchema) -> Newsletter:
        '''add a new subscriber'''

        new_subscriber = Newsletter(
            title="",
            content="",
            email=request.email)
        db.add(new_subscriber)
        db.commit()
        db.refresh(new_subscriber)

        return new_subscriber

    @staticmethod
    def check_existing_subscriber(db: Session, request: EmailSchema) -> Newsletter:
        """
        Check if user with email already exist
        """

        newsletter = db.query(Newsletter).filter(Newsletter.email==request.email).first()
        if newsletter:
            raise HTTPException(status_code=400, detail='User already subscribed to newsletter')

        return newsletter
    
    @staticmethod
    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all submisions with option to search using query parameters'''

        query = db.query(Newsletter)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Newsletter, column) and value:
                    query = query.filter(getattr(Newsletter, column).ilike(f'%{value}%'))

        return query.all()