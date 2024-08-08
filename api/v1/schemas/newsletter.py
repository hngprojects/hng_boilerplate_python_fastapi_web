from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailSchema(BaseModel):
    """
    pydantic model for data validation and serialization
    """

    email: EmailStr
    

class EmailRetrieveSchema(EmailSchema):

    class Config:
        from_attributes = True

class UpdateNewsletter(BaseModel):
    """
    represents the schema for the data to update the newsletter
    """
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None