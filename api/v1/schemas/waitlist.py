from pydantic import EmailStr, BaseModel

class WaitlistAddUserSchema(BaseModel):
    email: EmailStr
    full_name: str