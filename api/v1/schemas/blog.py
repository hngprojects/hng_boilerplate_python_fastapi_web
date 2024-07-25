from pydantic import BaseModel, Field
from uuid_extensions import uuid7
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class BlogCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str
    image_url: str = None
    tags: list[str] = None
    excerpt: str = Field(None, max_length=500)

class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    excerpt: Optional[str] = Field(None, max_length=500)

class BlogRequest(BaseModel):
    title: str
    content: str

class BlogUpdateResponseModel(BaseModel):
    status: str
    message: str
    data: dict

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
