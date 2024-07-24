from pydantic import BaseModel

class BlogRequest(BaseModel):
    title: str
    content: str

class BlogUpdateResponseModel(BaseModel):
    status: str
    message: str
    data: dict
