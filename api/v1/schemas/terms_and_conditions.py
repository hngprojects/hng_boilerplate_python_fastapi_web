from pydantic import BaseModel

class UpdateTermsAndConditions(BaseModel):
    title: str = None
    content: str = None

class DeleteResponseModel(BaseModel):
    message: str
    status_code: int
    success: bool
    data: dict
