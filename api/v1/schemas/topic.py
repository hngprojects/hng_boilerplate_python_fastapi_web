from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class TopicBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None


class TopicData(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    tags: Optional[list[str]] = None
    created_at: Optional[datetime] = None


class TopicList(BaseModel):
    status_code: int = 200
    success: bool
    message: str
    data: List[TopicData]
    
class TopicUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    
class TopicSearchSchema(BaseModel):
    query: str

class TopicDeleteSchema(BaseModel):
    id: str   