from pydantic import BaseModel, Field
from typing import Optional

class blogRequest(BaseModel):
    title: str
    content: str

class blogResponseModel(BaseModel):
    status: str
    message: str
    data: dict
