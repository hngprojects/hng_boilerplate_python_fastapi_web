from datetime import datetime
from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints


class CommentCreate(BaseModel):
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]

class CommentData(BaseModel):
    id: str
    user_id: str
    blog_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentSuccessResponse(BaseModel):
    status_code: int = 201
    message: str 
    success: bool = True
    data: CommentData

class CommentDislike(BaseModel):
    id: str
    comment_id: str
    user_id: str 
    ip_address: str
    created_at: datetime
    updated_at: datetime

class DislikeSuccessResponse(BaseModel):
    status_code: int = 201
    message: str 
    success: bool = True
    data: CommentDislike

class CommentLike(BaseModel):
    id: str
    comment_id: str
    user_id: str 
    ip_address: str
    created_at: datetime
    updated_at: datetime

class LikeSuccessResponse(BaseModel):
    status_code: int = 201
    message: str 
    success: bool = True
    data: CommentLike