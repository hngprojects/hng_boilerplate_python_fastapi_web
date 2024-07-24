# api/v1/services/notification_service.py
from sqlalchemy.orm import Session
from api.v1.models.notifications import Notification as NotificationModel
from api.v1.schemas.notificationschema import Notification as NotificationSchema

def get_user_notifications(user_id: int, db: Session):
    notifications = db.query(NotificationModel).filter(NotificationModel.user_id == user_id).all()
    return notifications
