from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from api.utils.dependencies import get_current_user, get_super_admin
from sqlalchemy.orm import Session
from api.v1.services.activity_log import ActivityLogService
from api.v1.models import User, ActivityLog
from api.db.database import get_db
from api.v1.schemas.activity_log import ActivityLogCreate, ActivityLogResponse, GetActivityLogResponse
from datetime import datetime


router = APIRouter()

@router.post("/activity-logs/create", response_model=ActivityLogResponse)
def create_activity_log(activity_log: ActivityLogCreate, db: Session = Depends(get_db)):
    service = ActivityLogService()

    db_user = db.query(User).filter(User.id == activity_log.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    created_activity_log = service.create(db, activity_log)

    response = ActivityLogResponse(
        id=str(created_activity_log.id),  # Adjust according to your model
        message="Activity log created successfully",
        status_code=201,  # HTTP status code for successful creation
        timestamp=datetime.utcnow()
    )
    
    return response

@router.get("/activity-logs/{user_id}", response_model=ActivityLogResponse)
def get_activity_logs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
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
   

@router.get("/activity-logs", response_model=List[GetActivityLogResponse])
def get_activity_log(
                    current_user: User = Depends(get_super_admin),
                     db: Session = Depends(get_db)):
    if current_user.is_super_admin:
        db_activity_logs = db.query(ActivityLog).all()
        return db_activity_logs
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You cannot access these."
        )
