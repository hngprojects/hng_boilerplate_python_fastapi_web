from typing import Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.notification_settings import NotificationSettings


class NotificationSettingsService(Service):
    '''Notification settings service functionality'''

    def create(self, db: Session, schema):
        '''Create new notification settings'''

        new_settings = NotificationSettings(**schema.dict())
        db.add(new_settings)
        db.commit()
        db.refresh(new_settings)

        return new_settings

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        return super().fetch_all()

    def fetch(self, db: Session, user_id: str):
        '''Fetches notification settings by user ID'''

        settings = check_model_existence(db, NotificationSettings, user_id)
        return settings

    def fetch_by_user(self, db: Session, user_id: str):
        '''Fetches notification settings for a specific user'''

        settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user_id).first()

        if settings is None:
            raise HTTPException(status_code=404, detail="Notification settings not found for the specified user")

        return settings

    def update(self, db: Session, user_id: str, schema):
        '''Updates notification settings'''

        settings = self.fetch_by_user(db=db, user_id=user_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)
        
        db.commit()
        db.refresh(settings)
        return settings

    def delete(self, db: Session, user_id: str):
        '''Deletes notification settings'''
        
        settings = self.fetch_by_user(db=db, user_id=user_id)
        db.delete(settings)
        db.commit()


notification_settings_service = NotificationSettingsService()