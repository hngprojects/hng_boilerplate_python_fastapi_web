from sqlalchemy.orm import Session
from api.v1.models.activity_logs import ActivityLog
from api.v1.models import User
from api.v1.schemas.activity_log import ActivityLogCreate

class ActivityLogService:
    '''ActivityLog service functionality'''

    def create(self, db: Session, schema: ActivityLogCreate):
        '''Create a new activity log'''
        new_activity_log = ActivityLog(**schema.dict())
        db.add(new_activity_log)
        db.commit()
        db.refresh(new_activity_log)
        return new_activity_log

    def get_user_by_id(self, db: Session, user_id: str):
        '''Retrieve a user by ID'''
        return db.query(User).filter(User.id == user_id).first()

    def get_activity_logs_by_user_id(self, db: Session, user_id: str):
        '''Retrieve activity logs for a specific user'''
        return db.query(ActivityLog).filter(ActivityLog.user_id == user_id).all()

    def get_all_activity_logs(self, db: Session):
        '''Retrieve all activity logs'''
        return db.query(ActivityLog).all()
