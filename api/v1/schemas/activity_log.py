from pydantic import BaseModel
from typing import List
from datetime import datetime
from uuid import UUID


class ActivityLog(BaseModel):
    log_id: str
    activity_type: str
    description: str
    timestamp: datetime
    
class ActivityLogCreate(ActivityLog):
    pass

class ActivityLogResponse(BaseModel):
    message: str
    status_code: int
    data: List[ActivityLog] = []



class ActivityLogResponse(ActivityLog):
    id: UUID
    timestamp: datetime

    class Config:
        orm_mode = True