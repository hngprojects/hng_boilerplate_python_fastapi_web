from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.db.database import get_db
from api.v1.models.notifications import Notification
from api.v1.models.user import User
from api.v1.schemas.notification import NotificationRequest, ResponseModel
from api.utils.email_service import send_mail
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
        
        
        
    async def send_email(self, request: NotificationRequest) -> ResponseModel:
        """
        Sends an email notification.

        Args:
            request (NotificationRequest): The request object containing email, subject, and message.

        Returns:
            ResponseModel: The response model indicating the success of the operation.
        """
        subject = request.subject
        recipient = request.email
        body = request.message

        send_mail(subject, recipient, body)
        
        return ResponseModel(
            success=True,
            status_code=200,
            message="Notification sent successfully",
            data={}
        )

    def delete(
        self,
        notification_id: str,
        user: User,
        db: Session = Depends(get_db),
    ):
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if notification.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to delete this notification")

        db.delete(notification)
        db.commit()
        db.refresh()

    def create(self):
        super().create()

    def fetch(self, db: Session):
        super().fetch()

    def fetch_all(self):
        super().fetch_all()

    def update(self):
        super().update()

notification_service = NotificationService()
