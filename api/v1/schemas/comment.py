from pydantic import BaseModel
from uuid import UUID


class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    blog_id: UUID
    content: str

    class Config:
        orm_mode = True