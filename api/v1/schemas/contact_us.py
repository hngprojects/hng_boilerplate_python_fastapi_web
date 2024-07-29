from pydantic import BaseModel, EmailStr


class CreateContactUs(BaseModel):
    """Validate the contact us form data."""

    full_name: str
    email: EmailStr
    phone_number: str
    message: str