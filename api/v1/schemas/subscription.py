from pydantic import BaseModel
from uuid import UUID

class SubscriptionRequest(BaseModel):
    id: UUID
