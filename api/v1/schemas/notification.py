from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str


class NotificationRead(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
