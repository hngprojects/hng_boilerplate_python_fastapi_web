from datetime import datetime
from typing_extensions import Annotated, List
from pydantic import BaseModel, StringConstraints, ConfigDict


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
    id: str = ""
    comment_id: str = ""
    user_id: str = ""
    ip_address: str = ""
    created_at: datetime = ""
    updated_at: datetime = ""

    model_config = ConfigDict(from_attributes=True)


class DislikeSuccessResponse(BaseModel):
    status_code: int = 201
    message: str
    success: bool = True
    data: CommentDislike


class LikeSchema(BaseModel):
    """
    Schema for likes
    """

    user_id: str = ""
    comment_id: str = ""

    model_config = ConfigDict(from_attributes=True)


class CommentsSchema(BaseModel):
    """
    Schema for Comments
    """

    user_id: str = ""
    blog_id: str = ""
    content: str = ""
    likes: List[LikeSchema] = []
    dislikes: List[CommentDislike] = []
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)


class CommentsResponse(BaseModel):
    """
    Schema for comments response
    """

    page: int = 1
    per_page: int = 20
    total: int = 0
    data: List[CommentsSchema] = []


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
