from sqlalchemy.orm import Session
from api.v1.models.activity_logs import ActivityLog


class ActivityLogService:
    '''Activity Log service'''

    def create_activity_log(self, db: Session, user_id: str, action: str):
        '''Creates a new activity log'''

        activity_log = ActivityLog(user_id=user_id, action=action)
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

    def get_all_activity_logs(self, db: Session):
        '''Retrieve all activity logs'''

        return db.query(ActivityLog).all()


activity_log_service = ActivityLogService()
