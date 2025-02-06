from datetime import datetime
from pydantic import (BaseModel, EmailStr,
                      model_validator, HttpUrl,
                      StringConstraints,
                      ConfigDict)
from typing import Optional, Annotated
from bleach import clean
import dns.resolver
from email_validator import validate_email, EmailNotValidError
import re
from api.v1.schemas.user import UserBase


def validate_mx_record(domain: str):
    """
    Validate mx records for email
    """
    try:
        # Try to resolve the MX record for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True if mx_records else False
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

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

    pronouns: Annotated[
        Optional[str],
        StringConstraints(max_length=20, strip_whitespace=True)
    ] = None
    job_title: Annotated[
        Optional[str],
        StringConstraints(max_length=60, strip_whitespace=True)
    ] = None
    username: Annotated[
        Optional[str],
        StringConstraints(max_length=30, strip_whitespace=True)
    ] = None
    department: Annotated[
        Optional[str],
        StringConstraints(max_length=60, strip_whitespace=True)
    ] = None
    social: Annotated[
        Optional[str],
        StringConstraints(max_length=60, strip_whitespace=True)
    ] = None
    bio: Annotated[
        Optional[str],
        StringConstraints(max_length=100, strip_whitespace=True)
    ] = None
    phone_number: Annotated[
        Optional[str],
        StringConstraints(max_length=14, strip_whitespace=True)
    ] = None
    recovery_email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl] = None
    facebook_link: Optional[HttpUrl] = None
    instagram_link: Optional[HttpUrl] = None
    twitter_link: Optional[HttpUrl] = None
    linkedin_link: Optional[HttpUrl] = None

    @model_validator(mode="before")
    @classmethod
    def phone_number_validator(cls, values: dict):
        """
        Validate data
        """
        phone_number = values.get('phone_number')
        recovery_email = values.get("recovery_email")

        if phone_number and not re.match(r"^\+?[1-9]\d{1,14}$", phone_number):
            raise ValueError("Please use a valid phone number format")
        
        if len(values) <= 0:
            raise ValueError("Cannot update profile with empty field")
        
        for key, value in values.items():
            if value:
                values[key] = clean(value)
        if recovery_email:
            try:
                recovery_email = validate_email(recovery_email, check_deliverability=True)
                if recovery_email.domain.count(".com") > 1:
                    raise EmailNotValidError("Recovery Email address contains multiple '.com' endings.")
                if not validate_mx_record(recovery_email.domain):
                    raise ValueError('Recovery Email is invalid')
            except EmailNotValidError as exc:
                raise ValueError(exc) from exc
            except Exception as exc:
                raise ValueError(exc) from exc

        return values

class ProfileData(BaseModel):
    """
    Pydantic model for a profile.
    """

    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    username: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    recovery_email: Optional[EmailStr] = None
    avatar_url: Optional[HttpUrl] = None
    facebook_link: Optional[HttpUrl] = None
    instagram_link: Optional[HttpUrl] = None
    twitter_link: Optional[HttpUrl] = None
    linkedin_link: Optional[HttpUrl] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdateResponse(BaseModel):
    """
    Schema for profile update response
    """
    message: str
    status_code: int
    data: ProfileData

class ProfileRecoveryEmailResponse(BaseModel):
    """
    Schema for recovery_email response
    """
    message: str
    status_code: int

class Token(BaseModel):
    """
    Token schema
    """
    token: Annotated[
        str,
        StringConstraints(
            min_length=30,
            strip_whitespace=True
        )
    ]
