from pydantic import BaseModel, EmailStr, Field

class CreateFAQInquiry(BaseModel):
    """Validate the FAQ Inquiry form data."""

    full_name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@gmail.com")
    message: str = Field(..., example="I have a question about the product.")