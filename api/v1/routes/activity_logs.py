from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.v1.models import User
from api.v1.models.activity_log import ActivityLog
from api.v1.schemas.activity_log import ActivityLogResponse,ActivityLogCreate
from api.db.database import get_db
from api.utils.dependencies import get_current_active_superuser
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



@router.get("activity-logs/{user_id}", response_model=ActivityLogResponse)
def get_activity_logs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Retrieve all activity logs for a specific user.
    Accessible only to superusers.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found: User ID does not exist"
        )

    activity_logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).all()
    return ActivityLogResponse(
        message="Activity logs retrieved successfully",
        status_code=200,
        data=activity_logs
    )
