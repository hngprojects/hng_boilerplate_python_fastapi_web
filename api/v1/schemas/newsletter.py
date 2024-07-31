from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """
    pydantic model for data validation and serialization
    """

    email: EmailStr
    

class EmailRetrieveSchema(EmailSchema):

    class Config:
        from_attributes = True