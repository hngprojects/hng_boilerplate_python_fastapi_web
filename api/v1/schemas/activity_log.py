from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List


class ActivityLogCreate(ActivityLog):
    pass


class ActivityLogResponse(ActivityLog):
    id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True

class ActivityLogBase(BaseModel):
    user_id: str
    action: str

class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(BaseModel):
    id: str
    message: str
    status_code: int
    data: List[ActivityLog] = []
    timestamp: datetime

    class Config:
        orm_mode = True
