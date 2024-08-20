from pydantic import (BaseModel, EmailStr,
                      model_validator, StringConstraints,
                      ConfigDict)
from typing import Annotated, Dict, List, Union, Optional




class RequestEmail(BaseModel):
    """
    Request shcema for forgot password
    """
    email: EmailStr


class ResetPasswordResponse(BaseModel):
    """
    Rsponse for reset password
    """
    message: str
    status_code: int


class UserData(BaseModel):
    """
    UserData schema
    """
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    is_verified: bool
    is_superadmin: bool
    is_deleted: bool
   
    model_config = ConfigDict(from_attributes=True)


class OrganizationData(BaseModel):
    """
    Organization Data schema
    """
    id: str
    name: str
    email: EmailStr
    industry: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
   
    model_config = ConfigDict(from_attributes=True)


class ResetPasswordSuccesful(BaseModel):
    """
    Rsponse for reset password
    """
    message: str
    status_code: int
    access_token: str
    data: Dict[str, Union[UserData, List[OrganizationData]]]
   
    @model_validator(mode='before')
    @classmethod
    def check_data_keys(cls, values: dict):
        """
        Validates data
        """
        data = values.get("data", {})
        if "user" not in data or "organisations" not in data:
            raise ValueError("Data must contain 'user' and 'organisations'")
        return values


class ResetPasswordRequest(BaseModel):
    reset_token: Annotated[
        str,
        StringConstraints(
            min_length=31
        )
    ]
    new_password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    confirm_password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]


    @model_validator(mode="before")
    @classmethod
    def password_validator(cls, values: dict):
        """
        Validate passwords
        """
        new_password: str = values.get("new_password")
        confirm_password: str = values.get("confirm_password")
       
        if new_password != confirm_password:
            raise ValueError("new password and confirm password must match")


        if new_password and new_password.strip():
            if not any(c.islower() for c in new_password):
                raise ValueError("Password must have at least one lowercase letter")
            if not any(c.isupper() for c in new_password):
                raise ValueError("Password must have at least one uppercase letter")
            if not any(c.isdigit() for c in new_password):
                raise ValueError("Password must have at least one digit")
            special_characters = "!@#$%&*()-_=:.?"
            if not any(c in special_characters for c in new_password):
                raise ValueError("Password must have at least one special character")
            if ' ' in new_password:
                raise ValueError("Password must not contain white space character")
        return values