from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class CustomerBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# class CreateCustomer(CustomerBase):
#     password: str

class CustomerResponse(CustomerBase):
    id: uuid.UUID

    class Config:
        orm_mode: True
