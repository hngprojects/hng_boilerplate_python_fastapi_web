from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from api.v1.schemas.comment import CommentData

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


class BlogBaseResponse(BaseModel):
    author_id: str
    title: str
    content: str
    image_url: Optional[str]
    is_deleted: bool
    excerpt: Optional[str]
    created_at: datetime
    updated_at: datetime
    views: int

    class Config:
        from_attributes = True

class BlogResponse(BlogBaseResponse):
    id: str
    tags: Optional[List[str]]

class BlogPostResponse(BlogBaseResponse):
    tags: Optional[str]


class BlogLikeDislikeCreate(BaseModel):
    id: str
    blog_id: str
    user_id: str
    ip_address: Optional[str]
    created_at: datetime

class BlogLikeDislikeCreateData(BaseModel):
    object: BlogLikeDislikeCreate
    objects_count: int  # number of likes/dislikes

class BlogLikeDislikeResponse(BaseModel):
    status_code: str
    message: str
    data: BlogLikeDislikeCreateData

class CommentRequest(BaseModel):
    content: str

class CommentUpdateResponseModel(BaseModel):
    status: str
    message: str
    data: CommentData


class BlogSearchResult(BaseModel):
    id: str
    title: str
    author: Optional[str]
    category: Optional[str]
    published_at: datetime
    tags: Optional[List[str]]
    excerpt: Optional[str]
    
    class Config:
        from_attributes = True

class BlogSearchResponse(BaseModel):
    status_code: int
    total_results: int
    blogs: List[BlogSearchResult]

