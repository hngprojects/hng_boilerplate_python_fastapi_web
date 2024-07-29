from pydantic import BaseModel

class ActivityLogCreate(BaseModel):
    user_id: int
    action: str
