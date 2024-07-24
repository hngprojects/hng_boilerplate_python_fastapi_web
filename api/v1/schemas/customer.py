from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SuccessResponse(BaseModel):
    status_code: int
    message: str
    data: dict
