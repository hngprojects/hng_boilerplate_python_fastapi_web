from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class BlogResponse(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    content: str
    image_url: Optional[str]
    tags: Optional[List[str]]
    is_deleted: bool
    excerpt: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DeleteBlogResponse(BaseModel):
    message: str
    status_code: int