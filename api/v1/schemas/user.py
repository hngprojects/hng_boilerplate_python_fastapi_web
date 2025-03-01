from email_validator import validate_email, EmailNotValidError
import dns.resolver
from datetime import datetime
from typing import (Optional, Union,
                    List, Annotated, Dict,
                    Literal)

from pydantic import (BaseModel, EmailStr,
                      field_validator, ConfigDict,
                      StringConstraints,
                      model_validator)
                      
from pydantic import Field  # Added this import

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

class UserBase(BaseModel):
    """Base user schema"""

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime


class UserCreate(BaseModel):
    """Schema to create a user"""

    email: EmailStr
    password: Annotated[
        str, StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        )
    ]
    """Added the confirm_password field to UserCreate Model"""
    confirm_password: Annotated[
        str, 
        StringConstraints(
            min_length=8,
            max_length=64,
            strip_whitespace=True
        ),
        Field(exclude=True)  # exclude confirm_password field
    ]
    first_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]
    last_name: Annotated[
        str, StringConstraints(
            min_length=3,
            max_length=30,
            strip_whitespace=True
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        password = values.get('password')
        confirm_password = values.get('confirm_password') # gets the confirm password
        email = values.get("email")

        # constraints for password
        if not any(c.islower() for c in password):
            raise ValueError("password must include at least one lowercase character")
        if not any(c.isupper() for c in password):
            raise ValueError("password must include at least one uppercase character")
        if not any(c.isdigit() for c in password):
            raise ValueError("password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in password):
            raise ValueError("password must include at least one special character")

        """Confirm Password Validation"""

        if not confirm_password:
            raise ValueError("Confirm password field is required")
        elif password != confirm_password:
            raise ValueError("Passwords do not match")
        
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        
        return values

class UserUpdate(BaseModel):
    
    first_name : Optional[str] = None
    last_name : Optional[str] = None

class UserData(BaseModel):
    """
    Schema for users to be returned to superadmin
    """
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_deleted: bool
    is_verified: bool
    is_superadmin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserData2(BaseModel):
    """
    Schema for users to be returned to superadmin
    """
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_deleted: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProfileData(BaseModel):
    """
    Pydantic model for a profile.
    """
    id: str
    created_at: datetime
    pronouns: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    social: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    recovery_email: Optional[EmailStr]

    model_config = ConfigDict(from_attributes=True)

class OrganisationData(BaseModel):
    """Base organisation schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    email: Optional[EmailStr] = None
    industry: Optional[str] = None
    user_role: List[str]
    type: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AuthMeResponse(BaseModel):
    """
    Auth response
    """
    message: str
    status_code: int
    data: Dict[Literal["user", "organisations", "profile"],
               Union[UserData2, List[OrganisationData], ProfileData]]


class AllUsersResponse(BaseModel):
    """
    Schema for all users
    """
    message: str
    status_code: int
    status: str
    page: int
    per_page: int
    total: int
    data: Union[List[UserData], List[None]]    

class AdminCreateUser(BaseModel):
    """
    Schema for admin to create a users
    """
    email: EmailStr
    first_name: str
    last_name: str
    password: str = ''
    is_active: bool = False
    is_deleted: bool = False
    is_verified: bool = False
    is_superadmin: bool = False

    model_config = ConfigDict(from_attributes=True)


class AdminCreateUserResponse(BaseModel):
    """
    Schema response for user created by admin
    """
    message: str
    status_code: int
    status: str
    data: UserData

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: str | None = None
    
    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        if not isinstance(values, dict):
            return values
        password = values.get('password')
        email = values.get("email")
        totp_code = values.get("totp_code")

        # constraints for password
        if not any(c.islower() for c in password):
            raise ValueError("password must include at least one lowercase character")
        if not any(c.isupper() for c in password):
            raise ValueError("password must include at least one uppercase character")
        if not any(c.isdigit() for c in password):
            raise ValueError("password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in password):
            raise ValueError("password must include at least one special character")
        
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        
        if totp_code:
            from api.v1.schemas.totp_device import TOTPTokenSchema
            
            if not TOTPTokenSchema.validate_totp_code(totp_code):
                raise ValueError("totp code must be a 6-digit number")
        
        return values


class EmailRequest(BaseModel):
    email: EmailStr

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validates email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    """Schema to structure token data"""

    id: Optional[str]


class DeactivateUserSchema(BaseModel):
    """Schema for deactivating a user"""

    reason: Optional[str] = None
    confirmation: bool


class ChangePasswordSchema(BaseModel):
    """Schema for changing password of a user"""

    old_password: Annotated[
        Optional[str],
        StringConstraints(min_length=8,
                          max_length=64,
                          strip_whitespace=True)
    ] = None

    new_password: Annotated[
        str,
        StringConstraints(min_length=8,
                          max_length=64,
                          strip_whitespace=True)
    ]

    confirm_new_password: Annotated[
        str,
        StringConstraints(min_length=8,
                          max_length=64,
                          strip_whitespace=True)
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_password(cls, values: dict):
        """
        Validates passwords
        """
        old_password = values.get('old_password')
        new_password = values.get('new_password')
        confirm_new_password = values.get("confirm_new_password")

        if (old_password and old_password.strip() == '') or old_password == '':
            values['old_password'] = None
        # constraints for old_password
        if old_password and old_password.strip():
            if not any(c.islower() for c in old_password):
                raise ValueError("Old password must include at least one lowercase character")
            if not any(c.isupper() for c in old_password):
                raise ValueError("Old password must include at least one uppercase character")
            if not any(c.isdigit() for c in old_password):
                raise ValueError("Old password must include at least one digit")
            if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in old_password):
                raise ValueError("Old password must include at least one special character")

        # constraints for new_password
        if not any(c.islower() for c in new_password):
            raise ValueError("New password must include at least one lowercase character")
        if not any(c.isupper() for c in new_password):
            raise ValueError("New password must include at least one uppercase character")
        if not any(c.isdigit() for c in new_password):
            raise ValueError("New password must include at least one digit")
        if not any(c in ['!','@','#','$','%','&','*','?','_','-'] for c in new_password):
            raise ValueError("New password must include at least one special character")
        
        if confirm_new_password != new_password:
            raise ValueError("New Password and Confirm New Password must match")
        
        return values


class ChangePwdRet(BaseModel):
    """schema for returning change password response"""

    status_code: int
    message: str


class MagicLinkRequest(BaseModel):
    """Schema for magic link creation"""

    email: EmailStr

    @model_validator(mode='before')
    @classmethod
    def validate_email(cls, values: dict):
        """
        Validate email
        """
        email = values.get("email")
        try:
            email = validate_email(email, check_deliverability=True)
            if email.domain.count(".com") > 1:
                raise EmailNotValidError("Email address contains multiple '.com' endings.")
            if not validate_mx_record(email.domain):
                raise ValueError('Email is invalid')
        except EmailNotValidError as exc:
            raise ValueError(exc) from exc
        except Exception as exc:
            raise ValueError(exc) from exc
        return values


class MagicLinkResponse(BaseModel):
    """Schema for magic link respone"""

    message: str

class UserRoleSchema(BaseModel):
    """Schema for user role"""

    role: str
    user_id: str
    org_id: str

    @field_validator("role")
    @classmethod
    def role_validator(cls, value):
        """
        Validate role
        """
        if value not in ["admin", "user", "guest", "owner"]:
            raise ValueError("Role has to be one of admin, guest, user, or owner")
        return value
