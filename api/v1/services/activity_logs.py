from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from api.v1.models.activity_logs import ActivityLog
from typing import Optional, Any



class ActivityLogService:
    """Activity Log service"""

    def create_activity_log(self, db: Session, user_id: str, action: str):
        """Creates a new activity log"""

        activity_log = ActivityLog(user_id=user_id, action=action)
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all products with option tto search using query parameters"""

        query = db.query(ActivityLog)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(ActivityLog, column) and value:
                    query = query.filter(
                        getattr(ActivityLog, column).ilike(f"%{value}%")
                    )
        
        return query.all()
    
    def delete_activity_log_by_id(self, db: Session, log_id: str):
        log = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity log with ID {log_id} not found"
            )

        db.delete(log)
        db.commit()

        return {"status": "success", "detail": f"Activity log with ID {log_id} deleted successfully"}


activity_log_service = ActivityLogService()
