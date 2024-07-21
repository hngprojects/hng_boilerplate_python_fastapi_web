from pydantic import BaseModel
from typing import List, Optional
import uuid

class CreateSubscriptionPlan(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    duration: str
    features: List[str]
    
    
class SubscriptionPlanResponse(CreateSubscriptionPlan):
    id: uuid.UUID
    
    class Config:
        orm_mode = True