from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ContactUsCreate(BaseModel):
    """Schema for creating a contact message."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)


class ContactUsResponse(BaseModel):
    """Schema for the response of a contact message."""

    id: str
    full_name: str
    email: EmailStr
    title: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
