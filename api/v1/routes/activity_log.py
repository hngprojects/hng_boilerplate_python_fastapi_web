from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.models import ActivityLog, User
from api.db.database import get_db
from api.v1.schemas.activity_log import ActivityLogCreate, ActivityLogResponse

router = APIRouter()

@router.post("/activity-logs/create", response_model=ActivityLogResponse)
def create_activity_log(activity_log: ActivityLogCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == activity_log.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_activity_log = ActivityLog(
        user_id=activity_log.user_id,
        action=activity_log.action,
        description=activity_log.description
    )
    db.add(db_activity_log)
    db.commit()
    db.refresh(db_activity_log)
    return db_activity_log
