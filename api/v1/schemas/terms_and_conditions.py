from pydantic import BaseModel

class UpdateTermsAndConditions(BaseModel):
    title: str = None
    content: str = None
