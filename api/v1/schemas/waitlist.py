from pydantic import BaseModel, EmailStr


class WaitlistUserCreate(BaseModel):
    email: EmailStr
    full_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "johndoe@gmail.com",
                "full_name": "John Doe"
            }
        }
