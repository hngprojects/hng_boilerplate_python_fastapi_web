from pydantic import BaseModel
from typing import List
from datetime import datetime


class ContactMessageResponse(BaseModel):
    full_name: str
    email: str
    title: str
    message: str

    class Config:
        orm_mode = True


class ContactMessageList(BaseModel):
    messages: List[ContactMessageResponse]
