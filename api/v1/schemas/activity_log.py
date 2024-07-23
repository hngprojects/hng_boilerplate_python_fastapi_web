from pydantic import BaseModel

class ActivityLogBase(BaseModel):
    user_id: int
    action: str
    description: str = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLogResponse(ActivityLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
