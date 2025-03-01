from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.squeeze import Squeeze
from api.core.dependencies.email_sender import send_email
from api.v1.schemas.squeeze import CreateSqueeze, FilterSqueeze
import asyncio

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
        
        # Fixed background task execution
        background_tasks.add_task(
            send_email,
            recipient=data.email,
            template_name='squeeze.html',
            subject='Welcome to HNG Squeeze',
            context={'name': data.full_name, 'cta_link': cta_link}
        )
        
        return new_squeeze

    def fetch_all(self, db: Session, filter: FilterSqueeze = None):
        """Fetch all squeeze pages"""
        if filter:
            return db.query(Squeeze).filter(Squeeze.status == filter.status).all()
        return db.query(Squeeze).all()

    def fetch(self, db: Session, id: str, filter: FilterSqueeze = None):
        """Fetch a specific squeeze page"""
        query = db.query(Squeeze).filter(Squeeze.id == id)
        if filter:
            query = query.filter(Squeeze.status == filter.status)
        return query.first()

    def update(self, db: Session, id: str, schema):
        """Update a specific squeeze page"""
        squeeze = db.query(Squeeze).filter(Squeeze.id == id).first()
        if not squeeze:
            raise HTTPException(status_code=404, detail="Squeeze page not found")

        for key, value in schema.dict(exclude_unset=True).items():
            setattr(squeeze, key, value)

        db.commit()
        db.refresh(squeeze)
        return squeeze

    def delete(self, db: Session, id: str):
        """Delete a specific squeeze page"""
        squeeze = db.query(Squeeze).filter(Squeeze.id == id).first()
        if not squeeze:
            raise HTTPException(status_code=404, detail="Squeeze page not found")
        
        db.delete(squeeze)
        db.commit()

    def delete_all(self, db: Session):
        """Delete all squeeze pages"""
        db.query(Squeeze).delete()
        db.commit()


squeeze_service = SqueezeService()

