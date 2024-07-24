from pydantic import BaseModel
from typing import List
from datetime import datetime


class ContactMessageBase(BaseModel):
    sender: str
    email: str
    message: str
    created_at: datetime
    updated_at: datetime


class ContactMessageResponse(ContactMessageBase):
    id: str

    class Config:
        orm_mode = True


class ContactMessageList(BaseModel):
    messages: List[ContactMessageResponse]
