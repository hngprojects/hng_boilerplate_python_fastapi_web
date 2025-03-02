from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


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

class NewsletterBase(BaseModel):
    title: str
    description: str
    content: str
    created_at: datetime
    updated_at: datetime

class SingleNewsletterResponse(BaseModel):
    """Schema for single newsletter
    """
    status_code: int = 200
    message: str
    success: bool = True
    data: NewsletterBase

class NewsletterSubscriber(BaseModel):
    id: str
    email: str
    subscribed_at: datetime

    class Config:
        from_attributes = True

class PaginatedNewsletterResponse(BaseModel):
    status_code: int = 200
    page: int
    per_page: int
    total_subscribers: int
    total_pages: int
    subscribers: List[NewsletterSubscriber]