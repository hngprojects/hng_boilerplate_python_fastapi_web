from sqlalchemy.orm import Session
from api.v1.models.activity_log import ActivityLog
from api.v1.schemas.activity_log import ActivityLogCreate

def create_activity_log(db: Session, activity_log: ActivityLogCreate):
    db_activity_log = ActivityLog(**activity_log.dict())
    db.add(db_activity_log)
    db.commit()
    db.refresh(db_activity_log)
    return db_activity_log
