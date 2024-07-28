from pydantic import BaseModel, EmailStr, Field


class RequestEmail(BaseModel):
    user_email: EmailStr

class ResetPassword(BaseModel):
    new_password: str = Field(min_length=8)
    confirm_new_password: str = Field(min_length=8)