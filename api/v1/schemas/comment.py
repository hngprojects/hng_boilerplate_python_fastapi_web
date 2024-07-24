from pydantic import BaseModel
from uuid import UUID


class CommentResponse(BaseModel):
    id: str
    user_id: str
    blog_id: str
    content: str

    class Config:
        orm_mode = True