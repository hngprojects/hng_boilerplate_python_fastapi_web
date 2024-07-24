from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    """
    Shared properties for a notification.

    Attributes:
        user_id (int): The ID of the user to whom the notification belongs.
        message (str): The content of the notification message.
        read_status (Optional[bool]): A flag indicating whether the
            notification has been read. Defaults to False.
    """
    user_id: int
    message: str
    read_status: Optional[bool] = False

class NotificationCreate(NotificationBase):
    """
    Properties required to create a new notification.

    Inherits:
        NotificationBase: Base properties shared across all notifications.
    """
    pass

class NotificationUpdate(NotificationBase):
    """
    Properties required to update an existing notification.

    Inherits:
        NotificationBase: Base properties shared across all notifications.

    Attributes:
        read_status (Optional[bool]): A flag indicating whether
            the notification has been read. This attribute is optional.
    """
    read_status: Optional[bool]

class NotificationInDBBase(NotificationBase):
    """
    Properties shared by models stored in the database.

    Inherits:
        NotificationBase: Base properties shared across all notifications.

    Attributes:
        id (int): The unique identifier for the notification.
        created_at (datetime): The time when the notification was created.
        updated_at (datetime): The time when the notification was last updated.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class Notification(NotificationInDBBase):
    """
    Properties to return to client.

    Inherits:
        NotificationInDBBase: Base properties shared across all notifications
            stored in the database.
    """
    pass

class NotificationInDB(NotificationInDBBase):
    """
    Properties stored in the database.

    Inherits:
        NotificationInDBBase: Base properties shared across all notifications
            stored in the database.
    """
    pass
