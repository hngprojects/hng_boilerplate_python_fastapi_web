from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.squeeze import Squeeze
from api.core.dependencies.email_sender import send_email
from api.v1.schemas.squeeze import CreateSqueeze, FilterSqueeze


class SqueezeService(Service):
    """Squeeze service"""

    def create(self, background_tasks: BackgroundTasks, db: Session, data: CreateSqueeze):
        """Create squeeze page"""
        new_squeeze = Squeeze(
            title=data.title,
            email=data.email,
            user_id=data.user_id,
            url_slug=data.url_slug,
            headline=data.headline,
            sub_headline=data.sub_headline,
            body=data.body,
            type=data.type,
            status=data.status,
            full_name=data.full_name,
        )
        db.add(new_squeeze)
        db.commit()
        db.refresh(new_squeeze)
        cta_link = 'https://anchor-python.teams.hng.tech/about-us'
        background_tasks.add_task(
            send_email, 
            recipient=data.email,
            template_name='squeeze.html',
            subject='Welcome to HNG Squeeze',
            context={
                'name': data.full_name,
                'cta_link': cta_link
            }
        )

        return new_squeeze

    def fetch_all(self, db: Session, filter: FilterSqueeze = None):
        """Fetch all squeeze pages"""
        squeezes = []
        if filter:
            squeezes = db.query(Squeeze).filter(Squeeze.status == filter.status).all()
        else:
            squeezes = db.query(Squeeze).all()
        return squeezes

    def fetch(self, db: Session, id: str, filter: FilterSqueeze = None):
        """Fetch a specific squeeze page"""
        squeeze = None
        if filter:
            squeeze = (
                db.query(Squeeze)
                .filter(Squeeze.id == id, Squeeze.status == filter.status)
                .first()
            )
        else:
            squeeze = db.query(Squeeze).filter(Squeeze.id == id).first()
        return squeeze

    def update(self, db: Session, id: str, schema):
        """Update a specific squeeze page"""
        pass

    def delete(self, db: Session, id: str):
        """Delete a specific squeeze page"""
        squeeze = db.query(Squeeze).filter(Squeeze.id == id).first()

        if not squeeze:
            raise HTTPException(status_code=404, detail="Squeeze page not found")
        
        db.delete(squeeze)
        db.commit()
        db.refresh()

    def delete_all(self, db: Session):
        """Delete all squeeze pages"""
        pass


squeeze_service = SqueezeService()
