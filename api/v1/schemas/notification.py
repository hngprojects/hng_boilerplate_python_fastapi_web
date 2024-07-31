from pydantic import BaseModel
from datetime import datetime


class NotificationBase(BaseModel):
    id: str
    title: str
    message: str
    status: str


class NotificationCreate(BaseModel):
    title: str
    message: str


class NotificationRead(NotificationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
