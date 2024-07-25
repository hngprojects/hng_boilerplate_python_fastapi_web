from sqlalchemy.orm import Session
from api.v1.schemas.newsletter import EMAILSCHEMA
from api.core.base.services import Service
from api.v1.models.newsletter import Newsletter


class NewsletterService(Service):
    '''Newsletter service functionality'''

    @staticmethod
    def create(db: Session, request: EMAILSCHEMA) -> Newsletter:
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
    def check_existing_subscriber(db: Session, request: EMAILSCHEMA) -> Newsletter:
        """
        Check if user with email already exist
        """

        return db.query(Newsletter).filter(Newsletter.email==request.email).first()