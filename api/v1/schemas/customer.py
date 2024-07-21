from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    organizations: List[UUID]

class SuccessResponse(BaseModel):
    status_code: int = 200
    current_page: int
    total_pages: int
    limit: int
    total_items: int
    data: List[CustomerBase]
