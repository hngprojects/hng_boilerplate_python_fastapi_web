from sqlalchemy.orm import Session
from api.v1.models.activity_logs import ActivityLog
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
