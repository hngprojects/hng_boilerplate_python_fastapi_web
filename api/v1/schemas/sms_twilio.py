from pydantic import BaseModel, Field, field_validator
import re

class SMSRequest(BaseModel):
    phone_number: str = Field(..., example="+1234567890")
    message: str = Field(..., example="Hello from HNG!")

    @field_validator('phone_number')
    def validate_phone_number(cls, value):
        phone_number_pattern = re.compile(r'^\+?[1-9]\d{8,14}$')
        if not phone_number_pattern.match(value):
            raise ValueError('Invalid phone number format')
        return value

    @field_validator('message')
    def validate_message(cls, value):
        if not value.strip():  
            raise ValueError('Message cannot be empty')
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "message": "Hello from HNG!"
            }
        }