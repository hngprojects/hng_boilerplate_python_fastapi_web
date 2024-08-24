from typing import List
from datetime import datetime
from pydantic import BaseModel


class ResponseBase(BaseModel):
    status_code: int = 200
    success: bool
    message: str


class PaginationBase(BaseModel):
    limit: int
    offset: int
    pages: int
    total_items: int
