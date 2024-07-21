from pydantic import BaseModel, EmailStr
from typing import Optional
from api.v1.models.customer import Customer
import uuid

# class CustomerBase(BaseModel):
#     username: str
#     email: EmailStr
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None

# class CreateCustomer(CustomerBase):
#     password: str

# class CustomerResponse(CustomerBase):
#     id: uuid.UUID

#     class Config:
#         orm_mode: True

class CustomerDeleteResponse(BaseModel):
    status: str
    message: str
