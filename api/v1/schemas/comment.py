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
