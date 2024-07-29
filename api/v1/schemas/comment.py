from pydantic import BaseModel, Field

class UpdateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class UpdateCommentResponse(BaseModel):
    status: str
    message: str
    status_code: int
    data: dict
