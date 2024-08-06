from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BlogCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str
    image_url: str = None
    tags: list[str] = None
    excerpt: str = Field(None, max_length=500)


class BlogRequest(BaseModel):
    title: str
    content: str


class BlogUpdateResponseModel(BaseModel):
    status: str
    message: str
    data: dict


class BlogResponse(BaseModel):
    id: str
    author_id: str
    title: str
    content: str
    image_url: Optional[str]
    tags: Optional[List[str]]
    is_deleted: bool
    excerpt: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogPostResponse(BaseModel):

    author_id: str
    title: str
    content: str
    image_url: Optional[str]
    is_deleted: bool
    excerpt: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogDislikeCreate(BaseModel):
    id: str
    blog_id: str
    user_id: str
    ip_address: Optional[str]
    created_at: datetime


class BlogDislikeResponse(BaseModel):
    status_code: str
    message: str
    data: BlogDislikeCreate
