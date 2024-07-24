from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID
from datetime import datetime


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


class Blog(BaseModel):
    id: UUID
    author_id: str
    title: str
    content: str
    image_url: Optional[List[HttpUrl]] = None
    is_deleted: bool
    excerpt: Optional[str] = None
    tags: Optional[List[str]] = None
    likes: Optional[int] = None
    dislikes: Optional[int] = None
    likes_audit: Optional[List[str]] = None
    dislikes_audit: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
