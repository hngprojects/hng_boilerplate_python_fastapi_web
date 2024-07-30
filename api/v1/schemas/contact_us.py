from pydantic import BaseModel, EmailStr


class ContactUsResponseSchema(BaseModel):
    full_name: str
    email: EmailStr
    title: str
    message: str

    class Config:
        from_attributes = True
