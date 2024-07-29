from pydantic import BaseModel

class ActivityLogCreate(BaseModel):
    user_id: str
    action: str
