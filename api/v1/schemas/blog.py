from pydantic import BaseModel, Field
from uuid_extensions import uuid7
from uuid import UUID
from datetime import datetime
from typing import List, Optional





class BlogCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str
    image_url: str = None
    tags: list[str] = None
    excerpt: str = Field(None, max_length=500)

class Blog(BlogCreate):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    excerpt: Optional[str] = Field(None, max_length=500)