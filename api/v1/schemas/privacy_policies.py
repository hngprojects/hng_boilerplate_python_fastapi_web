from pydantic import BaseModel

class PrivacyPolicyCreate(BaseModel):
    content: str

class PrivacyPolicyUpdate(BaseModel):
    content: str

class PrivacyPolicyResponse(BaseModel):
    id: int
    content: str

    class Config:
        from_attributes = True
