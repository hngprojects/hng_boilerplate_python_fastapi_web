from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ActivityLogBase(BaseModel):
    user_id: str
    action: str

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: str
    timestamp: datetime

    class Config:
        orm_mode = True
