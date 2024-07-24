from pydantic import BaseModel

class blogRequest(BaseModel):
    title: str
    content: str

class blogResponseModel(BaseModel):
    status: str
    message: str
    data: dict
