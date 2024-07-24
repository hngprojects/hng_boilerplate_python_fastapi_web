from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ActivityLogBase(BaseModel):
    user_id: UUID

    action: str
    description: str = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True
