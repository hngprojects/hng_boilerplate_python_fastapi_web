from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.squeeze import Squeeze
from api.v1.schemas.squeeze import CreateSqueeze, UpdateSqueeze


class SqueezeService(Service):
    """Squeeze service"""

    def create(self, db: Session, data: CreateSqueeze):
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
        return new_squeeze

    def fetch_all(self, db: Session):
        """Fetch all squeeze pages"""
        pass

    def fetch(self, db: Session, id: str):
        """Fetch a specific squeeze page"""
        pass

    def update(self, db: Session, id: str, data: UpdateSqueeze):
        """Update a specific squeeze page"""
        squeeze = db.query(Squeeze).filter(Squeeze.id == id).first()
        if squeeze:
            for key, value in data.model_dump().items():
                if value is not None:
                    setattr(squeeze, key, value)
            db.commit()
            db.refresh(squeeze)
            return squeeze
        return None

    def delete(self, db: Session, id: str):
        """Delete a specific squeeze page"""
        pass

    def delete_all(self, db: Session):
        """Delete all squeeze pages"""
        pass


squeeze_service = SqueezeService()
