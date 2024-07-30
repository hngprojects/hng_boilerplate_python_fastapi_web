from api.v1.models.base_model import BaseTableModel
from sqlalchemy import Column, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship


class NotificationSettings(BaseTableModel):
    __tablename__ = 'notification_settings'
    
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    email_notifications = Column(Boolean, nullable=False, default=True)
    sms_notifications = Column(Boolean, nullable=False, default=False)
    push_notifications = Column(Boolean, nullable=False, default=False)
    
    user = relationship("User", back_populates="notification_settings")

