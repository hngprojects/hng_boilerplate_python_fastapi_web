from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.notifications import Notification
from api.v1.models.user import User


class NotificationService(Service):
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

    def create(self):
        super().create()

    def delete(self):
        super().delete()

    def fetch(self, db: Session):
        super().fetch()

    def fetch_all(self):
        super().fetch_all()

    def update(self):
        super().update()


notification_service = NotificationService()
