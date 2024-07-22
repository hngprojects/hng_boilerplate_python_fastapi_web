from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class DeactivateUserSchema(BaseModel):
    '''Schema for deactivating a user'''

    reason: Optional[str] = None
    confirmation: bool

class RecoveryEmail(BaseModel):
    email: EmailStr

    @validator("email")
    def validate_email(cls, value):
        if not value:
            raise ValueError("Email is required")
        return value
    
class SuccessResponse(BaseModel):
    status_code: int = Field(200, example=200)
    message: str