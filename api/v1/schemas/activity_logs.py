from pydantic import BaseModel
from datetime import datetime


class ActivityLogCreate(BaseModel):
    user_id: int
    action: str


class ActivityLogResponse(BaseModel):
    action: str
    timestamp: datetime
