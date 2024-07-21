from pydantic import BaseModel
import uuid

class SubscriptionRequest(BaseModel):
    id: uuid.UUID
