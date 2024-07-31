from pydantic import BaseModel


class ReplyCreate(BaseModel):
    text: str