from pydantic import BaseModel
from typing import Any, Dict, Optional


# Pydantic models for request and response bodies
class NotificationSettings(BaseModel):
    email_notifications: Optional[bool]
    sms_notifications: Optional[bool]
    push_notifications: Optional[bool]