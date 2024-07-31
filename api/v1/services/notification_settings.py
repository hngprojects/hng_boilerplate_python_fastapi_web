from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.notifications import NotificationSetting
from api.v1.models.user import User
from api.v1.schemas.notification_settings import NotificationSettingsBase
from api.utils.db_validators import check_model_existence


class NotificationSettingService(Service):
    '''Notification settings service functionality'''

    def create(self, db: Session, user: User):
        '''Create a new notification setting for a user'''

        new_setting = NotificationSetting(user_id=user.id)
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)

        return new_setting
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all notification settings with option to search using query parameters'''

        query = db.query(NotificationSetting)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(NotificationSetting, column) and value:
                    query = query.filter(getattr(NotificationSetting, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, id: str):
        '''Fetches a notification service by id'''

        notification_setting = check_model_existence(db, NotificationSetting, id)
        return notification_setting
    

    def fetch_by_user_id(self, db: Session, user_id: str):
        '''Fetches a notification service by the user id of the user'''

        return db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
    

    def update(self, db: Session, user_id: str, schema: NotificationSettingsBase):
        '''Updates an notification service'''

        notification_setting = self.fetch_by_user_id(db=db, user_id=user_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(notification_setting, key, value)
        
        db.commit()
        db.refresh(notification_setting)
        return notification_setting
    

    def delete(self, db: Session, id: str):
        '''Deletes an notification service'''  
        pass


notification_setting_service = NotificationSettingService()
