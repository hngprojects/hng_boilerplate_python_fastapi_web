from sqlalchemy.orm import Session
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


activity_log_service = ActivityLogService()
