from pydantic import BaseModel, EmailStr


class AdminGet200Data(BaseModel):
    full_name: str
    email: EmailStr
    title: str
    message: str


class AdminGet200Response(BaseModel):
    status_code: int = 200
    status: str = "success"
    message: str = "Message retrieved successfully"
    data: dict
