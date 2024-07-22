from pydantic import BaseModel
from typing import Optional
# from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import UUID

class ProductSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float
    created_at: datetime
    updated_at: datetime