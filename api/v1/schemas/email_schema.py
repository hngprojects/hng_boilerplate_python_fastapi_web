from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    from_name: Optional[str] = None