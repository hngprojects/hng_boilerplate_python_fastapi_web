from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict
import re
from api.v1.schemas.user import UserBase

class ProfileBase(BaseModel):
    '''Base profile schema'''

    id: str
    created_at: datetime
    pronouns: str 
    job_title: str
    department: str
    social: str
    bio: str
    phone_number:str
    avatar_url:str
    recovery_email:Optional[EmailStr]
    user: UserBase


class ProfileCreateUpdate(BaseModel):
    '''Schema to create a profile'''
   
    pronouns: str 
    job_title: str
    department: str
    social: str
    bio: str
    phone_number:str
    avatar_url:str
    recovery_email:Optional[EmailStr]

    @field_validator('phone_number')
    def phone_number_validator(cls, value):
        if not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise ValueError('Please use a valid phone number format')
        return value
  


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    preferences: Optional[Dict[str, Optional[str]]] = None

class ProfileUpdate(BaseModel):
    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    recovery_email: Optional[EmailStr] = None

class UserAndProfileUpdate(UserProfileUpdate, ProfileUpdate):
    pass
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re
from api.v1.schemas.user import UserBase

class ProfileBase(BaseModel):
    """
    Pydantic model for a profile.

    This model is used for validating and serializing data related to a user's profile.
    It ensures that various fields are correctly formatted and handles optional fields.

    Attributes:
        id (str): The unique identifier of the profile.
        created_at (datetime): The date and time when the profile was created.
        pronouns (str): The pronouns of the user.
        job_title (str): The job title of the user.
        department (str): The department where the user works.
        social (str): The social media handle or URL of the user.
        bio (str): A brief biography of the user.
        phone_number (str): The user's phone number.
        avatar_url (str): The URL to the user's avatar image.
        recovery_email (Optional[EmailStr]): The user's recovery email address.
        user (UserBase): The user information associated with this profile.
        updated_at (datetime): The date and time when the profile was last updated.
    """
    id: str
    created_at: datetime
    pronouns: str
    job_title: str
    department: str
    social: str
    bio: str
    phone_number: str
    avatar_url: str
    recovery_email: Optional[EmailStr]
    user: UserBase
    

class ProfileCreateUpdate(BaseModel):
    """
    Pydantic model for creating or updating a profile.

    This model is used for validating and serializing data when creating or updating
    a user's profile in the system. It ensures that various fields are correctly formatted
    and handles optional fields for partial updates.

    Attributes:
        pronouns (Optional[str]): The pronouns of the user.
        job_title (Optional[str]): The job title of the user.
        department (Optional[str]): The department where the user works.
        social (Optional[str]): The social media handle or URL of the user.
        bio (Optional[str]): A brief biography of the user.
        phone_number (Optional[str]): The user's phone number.
        avatar_url (Optional[str]): The URL to the user's avatar image.
        recovery_email (Optional[EmailStr]): The user's recovery email address.
    """
    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    recovery_email: Optional[EmailStr] = None

    @field_validator("phone_number")
    @classmethod
    def phone_number_validator(cls, value):
        if value and not re.match(r"^\+?[1-9]\d{1,14}$", value):
            raise ValueError("Please use a valid phone number format")
        return value
