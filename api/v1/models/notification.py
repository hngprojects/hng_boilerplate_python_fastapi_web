#!/usr/bin/env python3
""" The Notification module Model Class
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func
    )
from sqlalchemy.orm import relationship
from api.v1.models.base_model import Base
from datetime import datetime

class Notification(Base):
    """
    Represents a notification in the system.

    Attributes:
        id (int): The unique identifier for the notification.
        user_id (int): The ID of the user to whom the notification belongs.
        message (str): The content of the notification.
        read_status (bool): A flag indicating whether the notification
                has been read. Defaults to False.
        created_at (datetime): The time when the notification was created.
                Defaults to the current time.
        updated_at (datetime): The time when the notification was last updated.
                Automatically updated to the current time when changes occur.
        user (User): The relationship to the User model.
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    read_status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="notifications")
