from pydantic import BaseModel

class BlogCategoryCreate(BaseModel):
    name: str


class BlogCategoryResponse(BaseModel):
    status: str
    message: str
    status_code: int