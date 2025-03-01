from pydantic import BaseModel, Field 
from typing import Annotated


class TOTPDeviceRequestSchema(BaseModel):
    """Schema for TOTP Device creation request"""
    
    user_id: str
    secret: str


class TOTPDeviceResponseSchema(BaseModel):
    """Schema for TOTP Device creation response"""
    
    secret: str
    otpauth_url: str
    qrcode_base64: str


class TOTPDeviceDataSchema(BaseModel):
    """Schema for representing TOTP Device data"""
    
    user_id: str
    confirmed: bool


class TOTPTokenSchema(BaseModel):
    """Schema for validating TOTP token provided by the user"""
    
    totp_token: Annotated[str, Field(min_length=6, max_length=6)]

    @classmethod
    def validate_totp_code(cls, code: str) -> bool:
        """Validates that the TOTP code is a 6-digit number"""
        
        if not code or len(code) != 6:
            return False
        try:
            int(code)
            return True
        except ValueError:
            return False