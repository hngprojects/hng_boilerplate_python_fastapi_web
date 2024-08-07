from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RequestEmail(BaseModel):
    user_email: EmailStr


class ResetPassword(BaseModel):
    new_password: str = Field(min_length=8)
    confirm_new_password: str = Field(min_length=8)

    @field_validator("new_password")
    def password_validator(cls, value):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            value,
        ):
            raise ValueError(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit and one special character."
            )
        return value
