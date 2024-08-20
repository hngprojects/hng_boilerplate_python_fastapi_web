from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Notification(BaseTableModel):
    __tablename__ = "notifications"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String, default="unread")  # unread, read

    user = relationship("User", back_populates="notifications", primaryjoin="Notification.user_id==User.id", foreign_keys=[user_id])


class NotificationSetting(BaseTableModel):
    __tablename__ = "notification_settings"

    mobile_push_notifications = Column(Boolean, server_default='false')
    email_notification_activity_in_workspace = Column(Boolean, server_default='false')
    email_notification_always_send_email_notifications = Column(Boolean, server_default='true')
    email_notification_email_digest = Column(Boolean, server_default='false')
    email_notification_announcement_and_update_emails = Column(Boolean, server_default='false')
    slack_notifications_activity_on_your_workspace = Column(Boolean, server_default='false')
    slack_notifications_always_send_email_notifications = Column(Boolean, server_default='false')
    slack_notifications_announcement_and_update_emails = Column(Boolean, server_default='false')

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="notification_setting")

