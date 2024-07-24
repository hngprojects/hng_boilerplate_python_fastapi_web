from pydantic import BaseModel, EmailStr


class EMAILSCHEMA(BaseModel):
    """
    pydantic model for data validation and serialization
    """
    email: EmailStr