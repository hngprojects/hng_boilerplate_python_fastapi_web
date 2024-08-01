from pydantic import BaseModel


class ReplyCreate(BaseModel):
    content: str
    