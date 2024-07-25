from api.v1.models.activity_logs import ActivityLog
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class ActivityLogCreate(BaseModel):
    user_id: str
    action: str


class GetActivityLogBase(BaseModel):
    user_id: str
    user: str = None
    action: str
    timestamp: datetime


class GetActivityLogResponse(GetActivityLogBase):
    user: None
    action: str
    timestamp: datetime


class ActivityLogBase(BaseModel):
    user_id: str
    action: str


class ActivityLogResponse(BaseModel):
    id: str
    message: str
    status_code: int
    timestamp: datetime


    class Config:
        orm_mode = True
