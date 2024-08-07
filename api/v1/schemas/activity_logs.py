from pydantic import BaseModel
from datetime import datetime



class ActivityLogCreate(BaseModel):
    user_id: str
    action: str


class ActivityLogResponse(BaseModel):
    action: str
    user_id: str
    timestamp: datetime
