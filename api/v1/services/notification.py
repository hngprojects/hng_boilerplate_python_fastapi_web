from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.notifications import Notification
from api.v1.models.user import User


class NotificationService(Service):

    def send_notification(
        self, title: str, message: str, db: Session = Depends(get_db)
    ):
        """Function to send a notification"""
        new_notification = Notification(title=title, message=message, status="unread")
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        return new_notification

    def mark_notification_as_read(
        self,
        notification_id: str,
        user: User,
        db: Session = Depends(get_db),
    ):
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user.id)
            .first()
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        # check if the notification is marked as read
        if notification.status == "read":
            return

        # update notification status
        notification.status = "read"

        # commit changes
        db.commit()
        db.refresh(notification)
        return notification

    def delete_notification(
        self,
        notification_id: str,
        user: User,
        db: Session = Depends(get_db),
    ):
        notification = (
            db.query(Notification).filter(Notification.id == notification_id).first()
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if notification.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this notification",
            )

        db.delete(notification)
        db.commit()
        db.refresh()

    def get_current_user_notifications(self, user: User, db: Session = Depends(get_db)):
        """Endpoint to get current user notifications"""

        return {"notifications": user.notifications}

    def fetch_notification_by_id(
        self, notification_id: str, db: Session = Depends(get_db)
    ):
        """Function to fetch any notification by ID"""
        notification = (
            db.query(Notification).filter(Notification.id == notification_id).first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    
    def fetch_all_notifications(self, db: Session):
        """Function to fetch all notifications"""
        notifications = db.query(Notification).all()
        return [notification.to_dict() for notification in notifications]

    def create(self):
        super().create()

    def fetch(self, db: Session):
        super().fetch()

    def fetch_all(self):
        super().fetch_all()

    def update(self):
        super().update()

    def delete(self):
        return super().delete()


notification_service = NotificationService()
