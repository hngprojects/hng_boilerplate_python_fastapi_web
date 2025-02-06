from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FAQBase(BaseModel):
    """Base schema for FAQ"""

    id: str
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime


class CreateFAQ(BaseModel):
    """Schema for creating FAQ"""

    question: str
    answer: str
    category: str


class UpdateFAQ(BaseModel):
    """Schema for updating FAQ"""

    question: Optional[str]
    answer: Optional[str]
    category: Optional[str]
