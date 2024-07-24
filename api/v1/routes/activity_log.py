from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.v1.services.activity_log import ActivityLogService
from api.v1.models import User, ActivityLog
from api.db.database import get_db
from api.v1.schemas.activity_log import ActivityLogCreate, ActivityLogResponse

router = APIRouter()

@router.post("/activity-logs/create", response_model=ActivityLogResponse)
def create_activity_log(activity_log: ActivityLogCreate, db: Session = Depends(get_db)):
    service = ActivityLogService()

    db_user = db.query(User).filter(User.id == activity_log.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    created_activity_log = service.create(db, activity_log)
    return created_activity_log
