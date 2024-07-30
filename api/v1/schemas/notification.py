from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationBase(BaseModel):
    id: str
    title: str
    message: str
    status: Optional[str] = "unread"
    
    

class NotificationCreate(BaseModel):
    title: str
    message: str


class ResponseModel(BaseModel):
    success: bool
    status_code: int
    message: str
    data: dict

class NotificationRead(NotificationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

