from pydantic import BaseModel


class ReplyCreate(BaseModel):
    """Reply pydantic model"""
    content: str
    