from typing import Optional
from pydantic import BaseModel, EmailStr


class ContactUsResponseSchema(BaseModel):
    full_name: str
    email: EmailStr
    title: str # Need review on this > to be converted to phone_number base on what I see on FE
    message: str

    class Config:
        from_attributes = True


class CreateContactUs(BaseModel):
    """Validate the contact us form data."""

    full_name: str
    email: EmailStr
    phone_number: str
    message: str
    org_id: Optional[str] = None
