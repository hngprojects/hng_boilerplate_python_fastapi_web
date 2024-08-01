from pydantic import EmailStr, BaseModel


class WaitlistAddUserSchema(BaseModel):
    """Pydantic Model for adding user to waitlist"""

    email: EmailStr
    full_name: str
