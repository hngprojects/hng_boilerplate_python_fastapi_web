from pydantic import BaseModel, EmailStr, Field
from typing import List
from sqlalchemy import Column, String, Integer
from api.v1.models.base import Base

class SqueezeForm(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    location: str
    job_title: str
    company: str
    interests: List[str]  # Updated to match the Squeeze model
    referral_source: str

class Squeeze(Base):
    __tablename__ = 'SqueezeForm'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    interests = Column(String, nullable=False)  # Adjusted to match the Pydantic model
    referral_source = Column(String, nullable=False)
